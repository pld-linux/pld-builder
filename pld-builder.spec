%define		snap	20141202
Summary:	PLD Linux RPM builder environment
Summary(pl.UTF-8):	Środowisko budowniczego pakietów RPM dla PLD
Name:		pld-builder
Version:	0.6.%{snap}
Release:	3
License:	GPL
Group:		Development/Building
Source0:	%{name}-%{version}.tar.bz2
# Source0-md5:	2fae9f6f0db55331306ed5351219fdcb
URL:		http://git.pld-linux.org/projects/pld-builder.new
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
Requires:	/usr/lib/sendmail
Requires:	bash
Requires:	bzip2
Requires:	crondaemon
Requires:	filesystem >= 3.0-33
Requires:	gnupg
Requires:	libuuid
Requires:	python
Requires:	python-pld-builder = %{version}-%{release}
Requires:	rc-scripts
Requires:	rsync
Requires:	sudo
Provides:	group(builder)
Provides:	user(builder)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/pld-builder
%define		_datadir	/usr/share/%{name}

# ensure these packaegs are never removed
%define keep_packages() { \
	f=/etc/rpm/sysinfo/Requirename; \
	for pkg in %*; do \
		grep -q "^$pkg$" $f && continue; \
		echo $pkg >> $f; \
	done; \
}

# remove packages from keep
%define undo_keep_packages() { \
	f=/etc/rpm/sysinfo/Requirename; \
	for pkg in %*; do \
		%{__sed} -i -e "/^$pkg$/d" $f; \
	done; \
}

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
Requires:	python-modules

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
Requires:	basesystem
Requires:	bash
Requires:	filesystem >= 3.0-33
Requires:	mount
Requires:	poldek >= 0.21-0.20070703.00.16
Requires:	rpm-build
Requires:	time
Requires:	tmpwatch
# NOTE: vserver-packages is usually hidden, so you must install it manually with --noignore
Requires:	vserver-packages
Provides:	group(builder)
Provides:	user(builder)
# for srpm builder
Requires:	git-core
Requires:	rpm-build-tools
Requires:	rpm-specdump

%description chroot
This is the package to be installed in builder chroot.

%description chroot -l pl.UTF-8
Ten pakiet należy zainstalować w środowisku chroot buildera.

%prep
%setup -q

for a in config/*.dist; do
	mv $a ${a%.dist}
done

%{__sed} -i -e '
	/^root_dir/s,=.*,= "%{_sharedstatedir}/%{name}",
	/^conf_dir/s,=.*,= "%{_sysconfdir}",
' PLD_Builder/path.py

%{__sed} -i -e '
	s,pld-linux\.org,example.org,g
	s,/spools/ready,/var/cache/%{name}/ready,
' config/builder.conf

%build
%{__make}
%py_lint PLD_Builder

%install
rm -rf $RPM_BUILD_ROOT

# python
install -d $RPM_BUILD_ROOT%{py_scriptdir}/PLD_Builder
cp -p PLD_Builder/*.py[co] $RPM_BUILD_ROOT%{py_scriptdir}/PLD_Builder

# other
install -d $RPM_BUILD_ROOT%{_sysconfdir}
cp -p config/{rsync-passwords,*.conf} $RPM_BUILD_ROOT%{_sysconfdir}
install -d $RPM_BUILD_ROOT%{_datadir}/{bin,admin}
for a in bin/*.sh; do
sed -e '
	/cd ~\/pld-builder.new/d
	s,python \(PLD_Builder.*.py\),python %{py_scriptdir}/\1c,
' $a > $RPM_BUILD_ROOT%{_datadir}/bin/$(basename $a)
done
cp -a admin/*.sh $RPM_BUILD_ROOT%{_datadir}/admin

# dirs
install -d $RPM_BUILD_ROOT{%{_sharedstatedir}/%{name}/{spool/{buildlogs,builds,ftp,notify},lock},/etc/{sysconfig,rc.d/init.d}}
install -d $RPM_BUILD_ROOT/home/services/builder/.gnupg
install -d $RPM_BUILD_ROOT/home/services/builder/.ssh
install -d $RPM_BUILD_ROOT/home/services/builder/rpm/{BUILD,RPMS,SRPMS,packages}
install -d $RPM_BUILD_ROOT/var/cache/%{name}/ready
ln -s %{_bindir}/builder $RPM_BUILD_ROOT/home/services/builder/rpm/packages

install -d $RPM_BUILD_ROOT/etc/poldek/repos.d
cp -p etc/poldek.conf $RPM_BUILD_ROOT/etc/poldek/repos.d/%{name}.conf

install -d $RPM_BUILD_ROOT/etc/rpm
cp -p etc/rpm.macros $RPM_BUILD_ROOT/etc/rpm/macros.builder

# crontab
install -d $RPM_BUILD_ROOT/etc/cron.d
cp -p etc/crontab $RPM_BUILD_ROOT/etc/cron.d/%{name}

# sudo
install -d $RPM_BUILD_ROOT/etc/sudoers.d
cp -p etc/sudo $RPM_BUILD_ROOT/etc/sudoers.d/%{name}

install -p etc/pld-builder.init $RPM_BUILD_ROOT/etc/rc.d/init.d/pld-builder
cp -p etc/pld-builder.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/pld-builder

# from admin/fresh-queue.sh
cd $RPM_BUILD_ROOT%{_sharedstatedir}/%{name}
install -d spool/{builds,buildlogs,notify,ftp} lock
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

%post chroot
%keep_packages pld-builder-chroot

%postun chroot
if [ "$1" = "0" ]; then
	%userremove builder
	%groupremove builder
	%undo_keep_packages pld-builder-chroot
fi

%files
%defattr(644,root,root,755)
%doc doc/{README,TODO,user-manual.txt}
%lang(pl) %doc doc/{jak-to-dziala.txt,jak-wysylac-zlecenia.txt}

%attr(754,root,root) /etc/rc.d/init.d/pld-builder
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/pld-builder

%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/cron.d/%{name}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sudoers.d/%{name}

%dir %{_sysconfdir}
%attr(640,root,builder) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*.conf
%attr(640,root,builder) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/rsync-passwords

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
%dir %attr(750,builder,builder) /home/services/builder/rpm/packages

# for srpm builder
%attr(750,builder,builder) /home/services/builder/rpm/packages/builder

# minimal but sane defaults for rpm inside chroot
%config(noreplace) %verify(not md5 mtime size) /etc/rpm/macros.builder

# locally cached rpms from bin-builder
%config(noreplace) %verify(not md5 mtime size) /etc/poldek/repos.d/%{name}.conf
%dir /var/cache/%{name}
%dir %attr(775,root,builder) /var/cache/%{name}/ready

%files -n python-pld-builder
%defattr(644,root,root,755)
%{py_scriptdir}/PLD_Builder
