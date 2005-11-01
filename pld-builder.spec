Summary:	PLD rpm builder environment
Summary(pl):	¦rodowisko budowniczego pakietów dla PLD
Name:		pld-builder
%define		_snap	20051101
Version:	0.0.%{_snap}
Release:	0.14
License:	GPL
Group:		Development/Building
Source0:	%{name}.new-%{_snap}.tar.bz2
# Source0-md5:	935e8edd4613686cfc88b793bfb6a6b6
URL:		http://cvs.pld-linux.org/cgi-bin/cvsweb/pld-builder.new/
BuildRequires:	python
Requires:	python-pld-builder = %{version}-%{release}
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/pld-builder
%define		_datadir	/usr/share/%{name}

%description
PLD rpm builder environment. This is the freshest "new" builder.

Other new and older attempts can be found from:
http://cvs.pld-linux.org/cgi-bin/cvsweb/pld-builder/
http://cvs.pld-linux.org/cgi-bin/cvsweb/pld-builder.old/
http://cvs.pld-linux.org/cgi-bin/cvsweb/builder_ng/

%description -l pl
¦rodowisko budowniczego pakietów dla PLD.

%package -n python-pld-builder
Summary:	PLD Builder
Group:		Development/Building
%pyrequires_eq	python-modules

%description -n python-pld-builder
PLD Builder python code.

%package client
Summary:	PLD Builder client
Group:		Development/Building
Requires:	gnupg

%description client
This is the client to send build requests to builders, it is usually
referred as STBR (Send To Builder Request).

%prep
%setup -q -n %{name}.new

sed -i -e '
	s,~/pld-builder.new/,%{_sharedstatedir}/%{name}/,
	/^conf_dir/s,=.*,= "%{_sysconfdir}/",

' PLD_Builder/path.py

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
# client
install -d $RPM_BUILD_ROOT%{_bindir}
install client/make-request.sh $RPM_BUILD_ROOT%{_bindir}/%{name}-make-request

# python
install -d $RPM_BUILD_ROOT%{py_scriptdir}/PLD_Builder
cp -a PLD_Builder/*.py[co] $RPM_BUILD_ROOT%{py_scriptdir}/PLD_Builder

# other
install -d $RPM_BUILD_ROOT%{_sysconfdir}
cp -a config/{rsync-passwords,*.conf} $RPM_BUILD_ROOT%{_sysconfdir}
install -d $RPM_BUILD_ROOT%{_datadir}/{bin,admin}
for a in bin/*.sh; do
sed -e '
#	s,cd ~/pld-builder.new,cd %{py_scriptdir},
	/cd ~\/pld-builder.new/d
	s,python \(PLD_Builder.*.py\),python %{py_scriptdir}/\1c,
' $a > $RPM_BUILD_ROOT%{_datadir}/bin/$(basename $a)
done
cp -a admin/*.sh $RPM_BUILD_ROOT%{_datadir}/admin

# dirs
install -d $RPM_BUILD_ROOT%{_sharedstatedir}/%{name}/{spool/{builds,ftp},lock,www/{s,}rpms}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README TODO
%lang(pl) %doc *.txt
%dir %{_sysconfdir}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*

%dir %{_datadir}
%dir %{_datadir}/bin
%attr(755,root,root) %{_datadir}/bin/*
%dir %{_datadir}/admin
%attr(755,root,root) %{_datadir}/admin/*

%dir %{_sharedstatedir}/%{name}
%dir %{_sharedstatedir}/%{name}/spool
%dir %{_sharedstatedir}/%{name}/spool/builds
%dir %{_sharedstatedir}/%{name}/spool/ftp
%dir %{_sharedstatedir}/%{name}/lock
%dir %{_sharedstatedir}/%{name}/www
%dir %{_sharedstatedir}/%{name}/www/rpms
%dir %{_sharedstatedir}/%{name}/www/srpms

%files client
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{name}-make-request

%files -n python-pld-builder
%defattr(644,root,root,755)
%{py_scriptdir}/PLD_Builder
