Summary:	PLD rpm builder environment
Summary(pl):	¦rodowisko budowniczego pakietów dla PLD
Name:		pld-builder
%define		_snap	20051101
Version:	0.0.%{_snap}
Release:	0.1
License:	GPL
Group:		Development/Building
Source0:	%{name}.new-%{_snap}.tar.bz2
# Source0-md5:	736f9e0dd3489a17c719625e5ff33d64
URL:		http://cvs.pld-linux.org/cgi-bin/cvsweb/pld-builder.new/
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/builder

%description
PLD rpm builder environment. This is the freshest "new" builder.

Other new and older attempts can be found from:
http://cvs.pld-linux.org/cgi-bin/cvsweb/pld-builder/
http://cvs.pld-linux.org/cgi-bin/cvsweb/pld-builder.old/
http://cvs.pld-linux.org/cgi-bin/cvsweb/builder_ng/

%description -l pl
¦rodowisko budowniczego pakietów dla PLD.

%package client
Summary:	PLD Builder client
Group:		Development/Building
Requires:	gnupg

%description client
This is the client to send build requests to builders, it is usually
referred as STBR (Send To Builder Request).

%prep
%setup -q -n %{name}.new

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir}
install client/make-request.sh $RPM_BUILD_ROOT%{_bindir}/%{name}-make-request

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README TODO
%lang(pl) %doc *.txt

%files client
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{name}-make-request
