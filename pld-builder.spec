%define		snap	20080713
Summary:	PLD RPM builder environment
Summary(pl.UTF-8):	Środowisko budowniczego pakietów RPM dla PLD
Name:		pld-builder
Version:	0.0.%{snap}
Release:	0.47
License:	GPL
Group:		Development/Building
Source0:	%{name}.new-%{snap}.tar.bz2
# Source0-md5:	954f612ed3c4d937d92090171f4eb4ed
Source1:	%{name}.init
Source2:	%{name}.sysconfig
URL:		http://cvs.pld-linux.org/cgi-bin/cvsweb/pld-builder.new/
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	bash
Requires:	crondaemon
Requires:	gnupg
Requires:	libuuid
Requires:	python-pld-builder = %{version}-%{release}
Requires:	rc-scripts
Provides:	group(builder)
Provides:	user(builder)
Provides:	user(ftpac)
Provides:	user(srpms_builder)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/pld-builder
%define		_datadir	/usr/share/%{name}

%description
PLD RPM builder environment. This is the freshest "new" builder.

Other new and older attempts can be found from:
http://cvs.pld-linux.org/cgi-bin/cvsweb/pld-builder/
http://cvs.pld-linux.org/cgi-bin/cvsweb/pld-builder.old/
http://cvs.pld-linux.org/cgi-bin/cvsweb/builder_ng/

%description -l pl.UTF-8
Środowisko budowniczego pakietów RPM dla PLD. To jest najnowszy "nowy"
builder.

Inne nowe i starsze próby można znaleźć pod:
http://cvs.pld-linux.org/cgi-bin/cvsweb/pld-builder/
http://cvs.pld-linux.org/cgi-bin/cvsweb/pld-builder.old/
http://cvs.pld-linux.org/cgi-bin/cvsweb/builder_ng/

%package -n python-pld-builder
Summary:	PLD Builder
Summary(pl.UTF-8):	Budowniczy PLD
Group:		Development/Building
%pyrequires_eq	python-modules

%description -n python-pld-builder
PLD Builder Python code.

%description -n python-pld-builder -l pl.UTF-8
Kod pythonowy budowniczego PLD.

%package chroot
Summary:	PLD Builder chroot
Summary(pl.UTF-8):	Środowisko chroot buildera PLD
Group:		Development/Building
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	bash
Requires:	rpm-build
Provides:	group(builder)
Provides:	user(builder)

%description chroot
This is the package to be installed in builder chroot.

%description chroot -l pl.UTF-8
Ten pakiet należy zainstalować w środowisku chroot buildera.

%package client
Summary:	PLD Builder client
Summary(pl.UTF-8):	Klient budowniczych PLD
Group:		Development/Building
Requires:	gnupg

%description client
This is the client to send build requests to builders, it is usually
referred as STBR (Send To Builder Request).

%description client -l pl.UTF-8
To jest klient do wysyłania zleceń na buildery, zwykle określanych
jako STBR (Send To Builder Request).

%prep
%setup -q -n %{name}.new

mv jak-wysy?a?-zlecenia.txt jak-wysylac-zlecenia.txt

%{__sed} -i -e '
	s,~/pld-builder.new/,%{_sharedstatedir}/%{name}/,
	/^conf_dir/s,=.*,= "%{_sysconfdir}/",

' PLD_Builder/path.py

%{__sed} -i -e 's,pld-linux\.org,example.org,g' config/builder.conf

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
install -d $RPM_BUILD_ROOT{%{_sharedstatedir}/%{name}/{spool/{buildlogs,builds,ftp,notify},lock,www/{s,}rpms},/etc/{sysconfig,rc.d/init.d}}
install -d $RPM_BUILD_ROOT/home/services/builder/.gnupg
install -d $RPM_BUILD_ROOT/home/services/builder/.ssh
install -d $RPM_BUILD_ROOT/home/services/builder/rpm/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/pld-builder
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/pld-builder

# from admin/fresh-queue.sh
cd $RPM_BUILD_ROOT%{_sharedstatedir}/%{name}
install -d spool/{builds,buildlogs,notify,ftp} www/srpms lock
echo 0 > www/max_req_no
echo 0 > spool/last_req_no
echo -n > spool/processed_ids
echo -n > spool/got_lock
echo '<queue/>' > spool/queue
echo '<queue/>' > spool/req_queue
if [ "$binary_builders" ]; then
	for bb in $binary_builders; do
		echo '<queue/>' > spool/queue-$bb
	done
fi

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 181 builder
%useradd -u 181 -g builder -c "srpms builder" srpms_builder
%useradd -u 182 -g builder -c "bin builder" -s /bin/bash -d /home/services/builder builder
%useradd -u 183 -g daemon -c "ftpac" ftpac

%pre chroot
%groupadd -g 181 builder
%useradd -u 182 -g builder -c "bin builder" -s /bin/bash -d /home/services/builder builder

%post
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
	%userremove srpms_builder
	%userremove builder
	%userremove ftpac
	%groupremove builder
fi

%postun chroot
if [ "$1" = "0" ]; then
	%userremove builder
	%groupremove builder
fi

%files
%defattr(644,root,root,755)
%doc README TODO
%doc user-manual.txt
%lang(pl) %doc jak-to-dziala.txt jak-wysylac-zlecenia.txt

%attr(754,root,root) /etc/rc.d/init.d/pld-builder
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/pld-builder

%dir %{_sysconfdir}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*

%dir %{_datadir}
%dir %{_datadir}/bin
%attr(755,root,root) %{_datadir}/bin/*
%dir %{_datadir}/admin
%attr(755,root,root) %{_datadir}/admin/*

%dir %{_sharedstatedir}/%{name}

%dir %attr(775,root,builder) %{_sharedstatedir}/%{name}/spool
%dir %attr(775,root,builder) %{_sharedstatedir}/%{name}/spool/buildlogs
%dir %attr(775,root,builder) %{_sharedstatedir}/%{name}/spool/builds
%dir %attr(775,root,builder) %{_sharedstatedir}/%{name}/spool/ftp
%dir %attr(775,root,builder) %{_sharedstatedir}/%{name}/spool/notify

%attr(644,builder,builder) %config(noreplace) %verify(not md5 mtime size) %{_sharedstatedir}/%{name}/spool/got_lock
%attr(644,builder,builder) %config(noreplace) %verify(not md5 mtime size) %{_sharedstatedir}/%{name}/spool/last_req_no
%attr(644,builder,builder) %config(noreplace) %verify(not md5 mtime size) %{_sharedstatedir}/%{name}/spool/processed_ids
%attr(644,builder,builder) %config(noreplace) %verify(not md5 mtime size) %{_sharedstatedir}/%{name}/spool/queue
%attr(644,builder,builder) %config(noreplace) %verify(not md5 mtime size) %{_sharedstatedir}/%{name}/spool/req_queue

%dir %attr(775,root,builder) %{_sharedstatedir}/%{name}/lock

%dir %{_sharedstatedir}/%{name}/www
%dir %{_sharedstatedir}/%{name}/www/rpms
%dir %{_sharedstatedir}/%{name}/www/srpms
%attr(644,builder,builder) %config(noreplace) %verify(not md5 mtime size) %{_sharedstatedir}/%{name}/www/max_req_no

%dir %attr(750,builder,builder) /home/services/builder
%dir %attr(750,builder,builder) /home/services/builder/.gnupg
%dir %attr(700,builder,builder) /home/services/builder/.ssh

%files chroot
%defattr(644,root,root,755)
%dir %attr(750,builder,builder) /home/services/builder
%dir %attr(750,builder,builder) /home/services/builder/rpm
%dir %attr(750,builder,builder) /home/services/builder/rpm/BUILD
%dir %attr(750,builder,builder) /home/services/builder/rpm/RPMS
%dir %attr(750,builder,builder) /home/services/builder/rpm/SOURCES
%dir %attr(750,builder,builder) /home/services/builder/rpm/SPECS
%dir %attr(750,builder,builder) /home/services/builder/rpm/SRPMS

%files client
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{name}-make-request

%files -n python-pld-builder
%defattr(644,root,root,755)
%{py_scriptdir}/PLD_Builder
