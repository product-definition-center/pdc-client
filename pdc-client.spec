# Enable Python 3 builds for Fedora
%if 0%{?fedora}
# If the definition isn't available for python3_pkgversion, define it
%{?!python3_pkgversion:%global python3_pkgversion 3}
%bcond_without  python3
%else
%bcond_with     python3
%endif

%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%{!?py2_build: %global py2_build %{expand: CFLAGS="%{optflags}" %{__python2} setup.py %{?py_setup_args} build --executable="%{__python2} -s"}}
%{!?py2_install: %global py2_install %{expand: CFLAGS="%{optflags}" %{__python2} setup.py %{?py_setup_args} install -O1 --skip-build --root %{buildroot}}}

Name:           pdc-client
Version:        1.2.0
Release:        4%{?dist}
Summary:        Console client for interacting with Product Definition Center
Group:          Development/Libraries
License:        MIT
URL:            https://github.com/product-definition-center/pdc-client
BuildArch:      noarch

Source0:        https://files.pythonhosted.org/packages/source/p/pdc-client/pdc-client-%{version}.tar.gz

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-nose
BuildRequires:  pytest
BuildRequires:  python-requests
BuildRequires:  python-requests-kerberos
BuildRequires:  python-mock
BuildRequires:  python2-beanbag

%if 0%{?with_python3}
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  python%{python3_pkgversion}-nose
BuildRequires:  python%{python3_pkgversion}-pytest
BuildRequires:  python%{python3_pkgversion}-requests
BuildRequires:  python3-requests-kerberos
BuildRequires:  python%{python3_pkgversion}-mock
BuildRequires:  python3-beanbag
%endif # if with_python3

%if (0%{?rhel} && 0%{?rhel} <= 6) || (0%{?centos} && 0%{?centos} <= 6)
BuildRequires:       python-unittest2
BuildRequires:       python-argparse
%endif

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
Requires:  python-requests-kerberos

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

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
find %{py3dir} -name '*.py' | xargs sed -i '1s|^#!python|#!%{__python3}|'
%endif # with_python3
find -name 'test_helpers_py3*'  -delete
find -name '*.py' | xargs sed -i '1s|^#!python|#!%{__python}|'

%build
%py2_build

%if 0%{?with_python3}
%py3_build
%endif # with_python3

%check
%{__python2} setup.py nosetests

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py nosetests
popd
%endif # with_python3

%install
%py2_install
%if 0%{?with_python3}
%py3_install
%endif # with_python3

mkdir -p %{buildroot}/%{_mandir}/man1
cp docs/pdc_client.1 %{buildroot}/%{_mandir}/man1/

# Move all plugins in upstream to /usr/share/pdc-client/
mkdir -p %{buildroot}/%{_datadir}/pdc-client/plugins
cp pdc_client/plugins/*  %{buildroot}/%{_datadir}/pdc-client/plugins

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
%dir %{_datadir}/pdc-client/plugins
%{_datadir}/pdc-client/plugins/*

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
