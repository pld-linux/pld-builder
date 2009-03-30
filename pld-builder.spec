%define		snap	20090330
Summary:	PLD RPM builder environment
Summary(pl.UTF-8):	Środowisko budowniczego pakietów RPM dla PLD
Name:		pld-builder
Version:	0.3.%{snap}
Release:	1
License:	GPL
Group:		Development/Building
Source0:	http://carme.pld-linux.org/~glen/%{name}-%{version}.tar.bz2
# Source0-md5:	c79d3ec2a45a917f3b59a475a5852ec8
Source1:	%{name}.init
Source2:	%{name}.sysconfig
URL:		http://cvs.pld-linux.org/cgi-bin/cvsweb/pld-builder.new/
BuildRequires:	python
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.469
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
Requires:	python
Requires:	python-pld-builder = %{version}-%{release}
Requires:	rc-scripts
Provides:	group(builder)
Provides:	user(builder)
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
Requires:	mount
Requires:	poldek >= 0.21-0.20070703.00.16
Requires:	rpm-build
Requires:	tmpwatch
Provides:	group(builder)
Provides:	user(builder)
# for srpm builder
Requires:	cvs-client
Requires:	rpm-build-tools

%description chroot
This is the package to be installed in builder chroot.

%description chroot -l pl.UTF-8
Ten pakiet należy zainstalować w środowisku chroot buildera.

%prep
%setup -q

mv jak-wysy?a?-zlecenia.txt jak-wysylac-zlecenia.txt

%{__sed} -i -e '
	s,~/pld-builder.new/,%{_sharedstatedir}/%{name}/,
	/^conf_dir/s,=.*,= "%{_sysconfdir}/",

' PLD_Builder/path.py

%{__sed} -i -e '
	s,pld-linux\.org,example.org,g
	s,/spools/ready,/var/cache/%{name}/ready,
' config/builder.conf

cat <<'EOF' > poldek.conf
# locally cached rpms
[source]
name = ready
pri  = -1
type = pndir
path = /var/cache/%{name}/ready
EOF

cat <<'EOF' > crontab
SHELL=/bin/sh
MAILTO=root

#* * * * * builder exec nice -n 19 %{_datadir}/bin/request-fetcher.sh
#* * * * * builder exec nice -n 19 %{_datadir}/bin/load-balancer.sh
#* * * * * builder exec nice -n 19 %{_datadir}/bin/file-sender.sh

#0 0 * * * chroot /home/users/builder/chroot-ac nice -n 19 tmpwatch -m 240 /var/cache/%{name}/ready
EOF

cat <<'EOF' > procmailrc
LOGFILE=procmail.log

#:0 c
#mail.copy

:0
* ^X-New-PLD-Builder:
| %{_datadir}/bin/request-handler.sh

:0
* ^FROM_MAILER
/dev/null

#:0
#!root@example.org
EOF

cat <<'EOF' > rpm.macros
# rpm macros for pld builder chroot

# A colon separated list of desired locales to be installed;
# "all" means install all locale specific files.
%%_install_langs en_US

# If non-zero, all erasures will be automagically repackaged.
%%_repackage_all_erasures    0

# Boolean (i.e. 1 == "yes", 0 == "no") that controls whether files
# marked as %doc should be installed.
# FIXME: excludedocs breaks kde build
#%%_excludedocs   1
EOF

%build
%{__make}
%py_lint PLD_Builder

%install
rm -rf $RPM_BUILD_ROOT

# python
install -d $RPM_BUILD_ROOT%{py_scriptdir}/PLD_Builder
cp -a PLD_Builder/*.py[co] $RPM_BUILD_ROOT%{py_scriptdir}/PLD_Builder

# other
install -d $RPM_BUILD_ROOT%{_sysconfdir}
cp -a config/{rsync-passwords,*.conf} $RPM_BUILD_ROOT%{_sysconfdir}
install -d $RPM_BUILD_ROOT%{_datadir}/{bin,admin}
for a in bin/*.sh; do
sed -e '
	/cd ~\/pld-builder.new/d
	s,python \(PLD_Builder.*.py\),python %{py_scriptdir}/\1c,
' $a > $RPM_BUILD_ROOT%{_datadir}/bin/$(basename $a)
done
cp -a admin/*.sh $RPM_BUILD_ROOT%{_datadir}/admin

# dirs
install -d $RPM_BUILD_ROOT{%{_sharedstatedir}/%{name}/{spool/{buildlogs,builds,ftp,notify},lock,www/{s,}rpms},/etc/{sysconfig,rc.d/init.d}}
install -d $RPM_BUILD_ROOT/home/services/builder/.gnupg
install -d $RPM_BUILD_ROOT/home/services/builder/.ssh
install -d $RPM_BUILD_ROOT/home/services/builder/rpm/{BUILD,RPMS,SRPMS,{SOURCES,SPECS}/CVS}
install -d $RPM_BUILD_ROOT/var/cache/%{name}/ready
ln -s %{_bindir}/builder $RPM_BUILD_ROOT/home/services/builder/rpm/SPECS

echo "SPECS" > $RPM_BUILD_ROOT/home/services/builder/rpm/SPECS/CVS/Repository
echo ":pserver:cvs@cvs.pld-linux.org:/cvsroot" > $RPM_BUILD_ROOT/home/services/builder/rpm/SPECS/CVS/Root
touch $RPM_BUILD_ROOT/home/services/builder/rpm/SPECS/CVS/Entries{,.Static}

install -d $RPM_BUILD_ROOT/etc/poldek/repos.d
cp -a poldek.conf $RPM_BUILD_ROOT/etc/poldek/repos.d/%{name}.conf

install -d $RPM_BUILD_ROOT/etc/rpm
cp -a rpm.macros $RPM_BUILD_ROOT/etc/rpm/macros.builder

# crontab
install -d $RPM_BUILD_ROOT/etc/cron.d
cp -a crontab $RPM_BUILD_ROOT/etc/cron.d/%{name}

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
%useradd -u 182 -g builder -c "bin builder" -s /bin/bash -d /home/services/builder builder

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
	%userremove builder
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

%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/cron.d/%{name}

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
%dir %attr(750,builder,builder) /home/services/builder/rpm/SRPMS
%dir %attr(750,builder,builder) /home/services/builder/rpm/SOURCES
%dir %attr(750,builder,builder) /home/services/builder/rpm/SPECS

# for srpm builder
%attr(750,builder,builder) /home/services/builder/rpm/SPECS/builder
%dir %attr(750,builder,builder) /home/services/builder/rpm/SPECS/CVS
%attr(640,builder,builder) %config(noreplace) %verify(not md5 mtime size) /home/services/builder/rpm/SPECS/CVS/Repository
%attr(640,builder,builder) %config(noreplace) %verify(not md5 mtime size) /home/services/builder/rpm/SPECS/CVS/Root
%attr(640,builder,builder) %config(noreplace) %verify(not md5 mtime size) /home/services/builder/rpm/SPECS/CVS/Entries
%attr(640,builder,builder) %config(noreplace) %verify(not md5 mtime size) /home/services/builder/rpm/SPECS/CVS/Entries.Static

# minimal but sane defaults for rpm inside chroot
%config(noreplace) %verify(not md5 mtime size) /etc/rpm/macros.builder

# locally cached rpms from bin-builder
%config(noreplace) %verify(not md5 mtime size) /etc/poldek/repos.d/%{name}.conf
%dir /var/cache/%{name}
%dir %attr(775,root,builder) /var/cache/%{name}/ready

%files -n python-pld-builder
%defattr(644,root,root,755)
%{py_scriptdir}/PLD_Builder
