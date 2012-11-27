Summary: User process module for Ganglia
Name: ganglia_ps
Version: 0.0.9
Release: 0
License: GPL
Group: System/monitoring
Vendor: Centre for eResearch, The University of Auckland
Packager: Martin Feller <m.feller@auckland.ac.nz>
BuildRequires: python >= 2.6
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}

%description

%prep

%setup 

%build

%install

rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
cp -r usr $RPM_BUILD_ROOT/
cp -r etc $RPM_BUILD_ROOT/
python -m compileall $RPM_BUILD_ROOT/usr

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/usr
/etc

