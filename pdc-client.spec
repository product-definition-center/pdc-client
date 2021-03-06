# Enable Python 3 builds for Fedora
# We could enable it for EPEL as well, but some dependencies (beanbag) are
# missing there.
# NOTE: do **NOT** change 'epel' to 'rhel' here, as this spec is also
# used to do RHEL builds without EPEL
%if 0%{?fedora}
# If the definition isn't available for python3_pkgversion, define it
%{?!python3_pkgversion:%global python3_pkgversion 3}
%bcond_without  python3
%else
%bcond_with     python3
%endif

# Compatibility with RHEL. These macros have been added to EPEL but
# not yet to RHEL proper.
# https://bugzilla.redhat.com/show_bug.cgi?id=1307190
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%{!?py2_build: %global py2_build %{expand: CFLAGS="%{optflags}" %{__python2} setup.py %{?py_setup_args} build --executable="%{__python2} -s"}}
%{!?py2_install: %global py2_install %{expand: CFLAGS="%{optflags}" %{__python2} setup.py %{?py_setup_args} install -O1 --skip-build --root %{buildroot}}}

%global plugin_install_path %{_datadir}/pdc-client/plugins

Name:           pdc-client
Version:        1.8.0
Release:        6%{?dist}
Summary:        Console client for interacting with Product Definition Center
Group:          Development/Libraries
License:        MIT
URL:            https://github.com/product-definition-center/pdc-client
BuildArch:      noarch

Source0:        https://files.pythonhosted.org/packages/source/p/pdc-client/pdc-client-%{version}.tar.gz

BuildRequires:  python2-devel
BuildRequires:  python2-beanbag

%if (0%{?rhel} && 0%{?rhel} <= 6) || (0%{?centos} && 0%{?centos} <= 6)
BuildRequires:  python-unittest2
BuildRequires:  python-argparse

BuildRequires:  python-setuptools
BuildRequires:  pytest
BuildRequires:  python-requests
BuildRequires:  python-requests-kerberos
BuildRequires:  python-mock
%else
BuildRequires:  python2-setuptools
BuildRequires:  python2-pytest
BuildRequires:  python2-requests
BuildRequires:  python2-requests-kerberos
BuildRequires:  python2-mock
%endif

%if 0%{?with_python3}
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  python%{python3_pkgversion}-pytest
BuildRequires:  python%{python3_pkgversion}-requests
BuildRequires:  python3-requests-kerberos
BuildRequires:  python%{python3_pkgversion}-mock
BuildRequires:  python3-beanbag
%endif # if with_python3

%if 0%{?with_python3}
Requires:  python%{python3_pkgversion}-pdc-client = %{version}-%{release}
%else
Requires:  python2-pdc-client = %{version}-%{release}
%endif

%description
This client package contains two separate Product Definition Center clients and
API module. Both clients contain extensive built-in help. Just run the
executable with -h or --help argument.

1. pdc_client

This is a very simple client. Essentially this is just a little more convenient
than using curl manually. Each invocation of this client obtains a token and
then performs a single request.

This client is not meant for direct usage, but just as a helper for integrating
with PDC from languages where it might be easier than performing the network
requests manually.

2. pdc

This is much more user friendly user interface. A single invocation can perform
multiple requests depending on what subcommand you used.

The pdc client supports Bash completion if argcomplete Python package is
installed.

3. Python API (pdc_client)

When writing a client code interfacing with PDC server, you might find
pdc_client module handy. It provides access to the configuration defined above
and automates obtaining authorization token.

%package -n python2-pdc-client
Summary:    Python 2 client library for Product Definition Center
%{?python_provide:%python_provide python2-pdc-client}
Requires:  python2-beanbag

%if (0%{?rhel} && 0%{?rhel} <= 6) || (0%{?centos} && 0%{?centos} <= 6)
Requires:  python-requests-kerberos
%else
Requires:  python2-requests-kerberos
%endif

%description -n python2-pdc-client
This is a python module for interacting with Product Definition Center
programatically. It can handle common authentication and configuration of PDC
server connections

%if 0%{?with_python3}
%package -n python%{python3_pkgversion}-pdc-client
Summary:    Python 3 client library for Product Definition Center

%{?python_provide:%python_provide python%{python3_pkgversion}-pdc-client}
Requires:  python3-beanbag
Requires:  python3-requests-kerberos

%description -n python%{python3_pkgversion}-pdc-client
This is a python module for interacting with Product Definition Center
programatically. It can handle common authentication and configuration of PDC
server connections
%endif # with_python3

%prep
%setup -q -n pdc-client-%{version}

# Replace installation plugin path in code
sed -i 's|^DEFAULT_PLUGIN_DIR = .*|DEFAULT_PLUGIN_DIR = "%{plugin_install_path}"|' \
        pdc_client/runner.py

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
find %{py3dir} -name '*.py' | xargs sed -i '1s|^#!python|#!%{__python3}|'
%endif # with_python3
find -name '*.py' | xargs sed -i '1s|^#!python|#!%{__python}|'

%build
%py2_build

%if 0%{?with_python3}
%py3_build
%endif # with_python3

%check
# Override plugin directory for tests.
export PDC_CLIENT_PLUGIN_PATH="%{buildroot}%{plugin_install_path}"
test -d "$PDC_CLIENT_PLUGIN_PATH"

# Smoke-test executables.
%if 0%{?with_python3}
export PYTHONPATH="%{buildroot}%{python3_sitelib}"
%else
export PYTHONPATH="%{buildroot}%{python_sitelib}"
%endif # with_python3
for executable in "%{buildroot}%{_bindir}"/*; do
    "$executable" --version
    "$executable" --help
done

# Run tests.
%{__python2} setup.py test -q

%if 0%{?with_python3}
    pushd %{py3dir}
    %{__python3} setup.py test -q
    popd
%endif # with_python3

%install
%py2_install
%if 0%{?with_python3}
%py3_install
%endif # with_python3

# Plugins are only required in the "pdc" script (not the Python packages). So
# move plugins to pdc-client package from Python package (this should also
# contain compiled bytecode).
mkdir -p %{buildroot}/%{plugin_install_path}
%if 0%{?with_python3}
mv -T %{buildroot}/%{python3_sitelib}/pdc_client/plugins %{buildroot}/%{plugin_install_path}
rm -r %{buildroot}/%{python_sitelib}/pdc_client/plugins
%else
mv -T %{buildroot}/%{python_sitelib}/pdc_client/plugins %{buildroot}/%{plugin_install_path}
%endif # with_python3

mkdir -p %{buildroot}/%{_mandir}/man1
cp docs/pdc_client.1 %{buildroot}/%{_mandir}/man1/

mkdir -p %{buildroot}/%{_sysconfdir}/bash_completion.d/
cp pdc.bash %{buildroot}/%{_sysconfdir}/bash_completion.d/

mkdir -p %{buildroot}/%{_sysconfdir}/pdc.d
cat > %{buildroot}/%{_sysconfdir}/pdc.d/fedora.json << EOF
{
    "fedora": {
        "host": "https://pdc.fedoraproject.org/rest_api/v1/",
        "develop": false,
        "ssl-verify": true
    }
}
EOF

%if 0%{?rhel} && 0%{?rhel} < 7
%global license %%doc
%endif

%files
%doc README.markdown
%{_mandir}/man1/pdc_client.1*
%{_sysconfdir}/bash_completion.d
%dir %{_sysconfdir}/pdc.d
%config(noreplace) %{_sysconfdir}/pdc.d/fedora.json
%{_bindir}/pdc
%{_bindir}/pdc_client
%dir %{_datadir}/pdc-client
%dir %{plugin_install_path}
%{plugin_install_path}/*

%if 0%{?with_python3}
# Omit installing Python 2 bytecode for Python 3.
%exclude %{plugin_install_path}/*.pyc
%exclude %{plugin_install_path}/*.pyo
%endif

%files -n python2-pdc-client
%doc README.markdown
%license LICENSE
%{python_sitelib}/pdc_client*

%if 0%{?with_python3}
%files -n python%{python3_pkgversion}-pdc-client
%doc README.markdown
%license LICENSE
%{python3_sitelib}/pdc_client*
%endif # with_python3


%changelog
* Thu Mar 01 2018 Iryna Shcherbina <ishcherb@redhat.com> - 1.8.0-6
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Dec 01 2017 Chuang Cao <chcao@redhat.com> 1.8.0-4
- Add the page_size=None when get auth (chcao@redhat.com)

* Wed Nov 29 2017 Chuang Cao <chcao@redhat.com> 1.8.0-3
- Rollback codes on parent class of PDCClient (chcao@redhat.com)

* Fri Nov 24 2017 Chuang Cao <chcao@redhat.com> 1.8.0-2
- Add new version 1.8.0 in setup.py (chcao@redhat.com)
- Remove "setup.py test" part from sepc file (chcao@redhat.com)

* Wed Nov 22 2017 Chuang Cao <chcao@redhat.com> 1.8.0-1
- Add PDCClient tests and fix the discovered bugs (lholecek@redhat.com)
- Add comments for rpm requirements (chcao@redhat.com)
- Get the endpoint as attr which includes "-" (chcao@redhat.com)
- Fix wrapping BeanBag methods and operators (lholecek@redhat.com)
- Fix bug of Multipaged (chcao@redhat.com)
- Add MultiPageBeanBag class to support get multi pages (chcao@redhat.com)
- Add the close function when load plugins (chcao@redhat.com)
- Correct the flake8 issues (chcao@redhat.com)
- Change the docstrings and fix issues (chcao@redhat.com)
- Remove duplicate code (lholecek@redhat.com)
- Update documentation (lholecek@redhat.com)
- Add documentation link to README file (lholecek@redhat.com)
- Add discription of page_size=-1 in help doc (chcao@redhat.com)
- Fix printing errors and exit code for pdc_client (lholecek@redhat.com)
- Add smoke-test for all executables (lholecek@redhat.com)
- Fix running tests when building rpm (lholecek@redhat.com)
- Override plugin paths with PDC_CLIENT_PLUGIN_PATH (lholecek@redhat.com)
- Improve installing plugins (lholecek@redhat.com)
- Revert removing comments from downstream (lholecek@redhat.com)
- Add the page argument on pdc (chcao@redhat.com)

* Fri Sep 08 2017 Lukas Holecek <lholecek@redhat.com> 1.7.0-3
- Fix printing help for missing sub-commands (lholecek@redhat.com)
- Fix "pdc_client --version" (lholecek@redhat.com)

* Mon Aug 28 2017 Lukas Holecek <lholecek@redhat.com> 1.7.0-2
- Omit installing plugins with Python packages

* Tue Aug 22 2017 Lukas Holecek <lholecek@redhat.com> 1.7.0-1
- Bump versin in setup.py (lholecek@redhat.com)
- Update spec file from downstream (lholecek@redhat.com)
- Bug fix for ssl_verify in old pdc_client (chuzhang@redhat.com)
- Fix content-delivery-repo list ordering (lholecek@redhat.com)
- Print table with minimum width for content-deliver-repo list
  (lholecek@redhat.com)
- Update test data for content-deliver-repo (lholecek@redhat.com)
- Update value type for "Shadow" field (lholecek@redhat.com)
- Increase `pdc content-deliver-repo list` verbosity. (dmach@redhat.com)
- Fix passing ordering parameter (lholecek@redhat.com)
- Make error reporting less verbose (lholecek@redhat.com)
- Omit printing long HTML with error (lholecek@redhat.com)
- Remove unused import (lholecek@redhat.com)
- Simplify reporting server errors. (dmach@redhat.com)
- Modify base_product plugin according to commit 79cbe98 (chuzhang@redhat.com)
- Sort commands in pdc --help. (dmach@redhat.com)
- Remove the arch parameter from option (chcao@redhat.com)
- Use local development plugin directory (lholecek@redhat.com)
- Add content-delivery-repo export/import sub-commands. (dmach@redhat.com)
- Unify json output serialization. (dmach@redhat.com)
- Add base-product command (chcao@redhat.com)
- Add base-product command. (dmach@redhat.com)
- Allow deleting multiple repos at once. (dmach@redhat.com)
- Allow deleting multiple group resource perms at once. (dmach@redhat.com)
- Fix running tests with Travis (lholecek@redhat.com)
- Replace a custom test runner with standard setup.py test. (dmach@redhat.com)
- Allow deleting release variants. (dmach@redhat.com)
- Add "release-variant" command (chcao@redhat.com)
- Add "release-variant" command. (dmach@redhat.com)
- OrderedDict support in python 2.6 (chcao@redhat.com)
- Add "product-version" command. (dmach@redhat.com)
- OrderedDict support in python 2.6 (chcao@redhat.com)
- Add "product" command. (dmach@redhat.com)
- plugin_helpers: Allow overriding 'dest' option. (dmach@redhat.com)
- Fix reading "develop" option from settings (lholecek@redhat.com)
- Fix configuration name in README (lholecek@redhat.com)
- Fix the Sphix dependency (caochuangxiang@gmail.com)
- Change the new token secure with chcao (caochuangxiang@gmail.com)
- Feedback: incorrect place to specify default SSL behavior (ahills@redhat.com)
- Fix SSL command line options (ahills@redhat.com)
- Surport SSL cert when swith insecure to false (bliu@redhat.com)
- Fix the bug about the include-shadow para in repo clone (bliu@redhat.com)

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jun 21 2017 Lubomír Sedlář <lsedlar@redhat.com> - 1.2.0-3
- Fix dependencies on Python 3

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Dec 27 2016 bliu <bliu@redhat.com> 1.2.0-1
- Fix the porblem in repo clone (ycheng@redhat.com)
- Add the SSL and remove the Warning Info (bliu@redhat.com)
- Add RPC "clone" command to content-delivery-repo (ahills@redhat.com)
- Bug about ssl verify (bliu@redhat.com)
- Add a new plugin of group-resource-permission (bliu@redhat.com)
- Support option --server as well. (chuzhang@redhat.com)
- Add insecure configuration option back with a warning (ahills@redhat.com)
- Fix PEP8 violation (ahills@redhat.com)
- More flexible SSL certificate verification configuration (ahills@redhat.com)
- Create a new plugin of compose-full-import (bliu@redhat.com)
- Update the SPEC file (bliu@redhat.com)
- Update the README.markdown file in pdc-client repo (bliu@redhat.com)
- Merge plugins in config file with default plugins. (chuzhang@redhat.com)
- fix TypeError: unorderable types: NoneType() <= int() (jpopelka@redhat.com)
- [spec] Python3 build (jpopelka@redhat.com)
- update the requirements file with flake<=3.0.3 (bliu@redhat.com)
- Update the SPEC file for removing the directories. (bliu@redhat.com)

* Mon Dec 19 2016 Miro Hrončok <mhroncok@redhat.com> - 1.1.0-3
- Rebuild for Python 3.6

* Fri Aug 12 2016 Jiri Popelka <jpopelka@redhat.com> - 1.1.0-2
- Python3 build

* Sun Aug 07 2016 bliu <bliu@redhat.com> 1.1.0-1
- When page_size <= 0; the pagination will be disabled. (bliu@redhat.com)
- Handle page_size in mocked API calls. (nils@redhat.com)
- Move necessary arguments to required argument list. (ycheng@redhat.com)
- Make format strings compatible with python 2.6 (chuzhang@redhat.com)
- Fix failure with requests-kerberos 0.9+ and Python 3 (drop monkey_patch.py)
  (mzibrick@redhat.com)
- Add FILES section and fix issue link in manpage (sochotnicky@redhat.com)

* Sun Jul 17 2016 bliu <bliu@redhat.com> 1.0.0-2
- Move plugins outside of python_sitelib. (bliu@redhat.com)
- Allow specifying plugins in the config file. (chuzhang@redhat.com)
- Change configuration files for pdc-client. (bliu@redhat.com)
- Add field 'subvariant' to image sub-command. (ycheng@redhat.com)

* Thu May 05 2016 bliu <bliu@redhat.com> 0.9.0-3
- Change filtering arguments's underscore to minus to be consistent.
  (ycheng@redhat.com)
- Modify compose-tree-locations in client because API url changed.
  (ycheng@redhat.com)
- Add support for repo manipulation into pdc client (ycheng@redhat.com)

* Fri Feb 26 2016 bliu <bliu@redhat.com> 0.9.0-1
- Add headers in result for pdc client output. (ycheng@redhat.com)
- Add pdc client project page and PyPI release docomentation.
  (ycheng@redhat.com)
- Update the error info (bliu@redhat.com)
- Update the more detail info (bliu@redhat.com)
- Add error info when input irregular or illegal para (bliu@redhat.com)
- Let pdc client handle pdc warning header (ycheng@redhat.com)
- Pypi setup (sochotnicky@redhat.com)
- Fix release component update logging type (sochotnicky@redhat.com)

* Wed Jan 13 2016 bliu <bliu@redhat.com> 0.2.0-3
- PATCH on build-image-rtt-tests with build_nvr/format (bliu@redhat.com)
- Add beanbag required version. (xchu@redhat.com)
- Add header for build image in new pdc client output (ycheng@redhat.com)
- Add tests for permission list. (xchu@redhat.com)
- Add test for build-image detail. (xchu@redhat.com)
- Add support for compose-tree-locations. (chuzhang@redhat.com)
- Add head in result when running build_image_rtt_tests (bliu@redhat.com)
- Use new get_paged method instead of deprecated one. (ycheng@redhat.com)
- Pdc client add support for build-image-rtt-tests (bliu@redhat.com)
- Add support for compose-image-rtt-tests in pdc client (ycheng@redhat.com)
- Make mocked endpoints possibly callable. (rbean@redhat.com)
- Add help message for 'active' filter. (xchu@redhat.com)
- Enable page_size in new pdc client (bliu@redhat.com)

* Wed Jan 13 2016 bliu <bliu@redhat.com> 0.2.0-2

* Fri Dec 04 2015 Xiangyang Chu <xchu@redhat.com> 0.2.0-1
- Add python 2.6 check. (xchu@redhat.com)
- Fix spec URL (rbean@redhat.com)
- Allow PDCClient to be configured with arguments. (rbean@redhat.com)
- Imporvements on new `pdc` client.
* Fri Sep 11 2015 Xiangyang Chu <xychu2008@gmail.com> 0.1.0-1
- new package built with tito
