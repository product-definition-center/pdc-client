%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}


Name:           pdc-client
Version:        0.9.0
Release:        1%{?dist}
Summary:        Console client for interacting with Product Definition Center
Group:          Development/Libraries
License:        MIT
URL:            https://github.com/product-definition-center/pdc-client
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  python
Requires:       python-requests
Requires:       python-requests-kerberos
Requires:       beanbag >= 1.9.2


%description
This package contains a console client for interacting with Product Definition
Center (PDC)


%prep
%setup -q -n %{name}-%{version}


%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/%{python_sitelib}/pdc_client
cp -R pdc_client/* %{buildroot}/%{python_sitelib}/pdc_client

mkdir -p %{buildroot}%{_defaultdocdir}/pdc_client

# Install PDC client command line interface
install -m 0644 -D -p bin/pdc_client %{buildroot}%{_bindir}/pdc_client
install -m 0644 -D -p bin/pdc %{buildroot}%{_bindir}/pdc

# Install pdc bash argcompletion file
install -m 0644 -D -p pdc.bash %{buildroot}%{_sysconfdir}/bash_completion.d/pdc.bash

install -m 0644 -D -p docs/pdc_client.1 %{buildroot}%{_mandir}/man1/pdc_client.1
gzip %{buildroot}%{_mandir}/man1/pdc_client.1


%files
%{python_sitelib}/pdc_client
%attr(755, root, root) %{_bindir}/pdc_client
%attr(755, root, root) %{_bindir}/pdc
%{_mandir}/man1/pdc_client.1.gz
%{_sysconfdir}/bash_completion.d/pdc.bash


%changelog
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
- 

* Fri Dec 04 2015 Xiangyang Chu <xchu@redhat.com> 0.2.0-1
- Add python 2.6 check. (xchu@redhat.com)
- Fix spec URL (rbean@redhat.com)
- Allow PDCClient to be configured with arguments. (rbean@redhat.com)
- Imporvements on new `pdc` client.
* Fri Sep 11 2015 Xiangyang Chu <xychu2008@gmail.com> 0.1.0-1
- new package built with tito

