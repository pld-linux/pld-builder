Summary:	PLD rpm builder environment
Summary(pl):	¦rodowisko budowniczego pakietów dla PLD
Name:		pld-builder
Version:	1.1
Release:	1
License:	GPL
Group:		Development/Building
Group(pl):	Programowanie/Budowanie
Source0:	ftp://ftp.pld.org.pl/packages/%{name}-%{version}.tar.gz
Requires:	smtpdaemon
Requires:	crondaemon
Requires:	procmail
Requires:	rpm
Requires:	gnupg
Requires:	textutils
Requires:	sed
Requires:	grep
Requires:	sudo
Requires:	sh-utils
Requires:	util-linux
Requires:	fileutils
Requires:	openssh
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
PLD rpm builder environment.

%description -l pl
¦rodowisko budowniczego pakietów dla PLD.

%prep
%setup -q

%build
echo "ARCH=%{_target_cpu}" >> .builderrc
echo "ARCH=%{_target_cpu}" >> chroot/.builderrc

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/home/users/builder/{.requests-%{_target_cpu},bin} \
	$RPM_BUILD_ROOT/home/users/builder/chroot-%{_target_cpu}/home/users/builder/bin \
	$RPM_BUILD_ROOT/etc/cron.d

install .builderrc $RPM_BUILD_ROOT/home/users/builder/
install .procmailrc $RPM_BUILD_ROOT/home/users/builder/
install bin/* $RPM_BUILD_ROOT/home/users/builder/bin/

install chroot/.builderrc $RPM_BUILD_ROOT/home/users/builder/chroot-%{_target_cpu}/home/users/builder/
install chroot/.rpmmacros $RPM_BUILD_ROOT/home/users/builder/chroot-%{_target_cpu}/home/users/builder/
%ifarch %{ix86}
install chroot/.rpmrc.%{_target_cpu} $RPM_BUILD_ROOT/home/users/builder/chroot-%{_target_cpu}/home/users/builder/.rpmrc
%endif
install chroot/bin/* $RPM_BUILD_ROOT/home/users/builder/chroot-%{_target_cpu}/home/users/builder/bin/

mv $RPM_BUILD_ROOT/home/users/builder/bin/buildrpm-cron $RPM_BUILD_ROOT/home/users/builder/bin/buildrpm-cron.bak
cat > $RPM_BUILD_ROOT/home/users/builder/bin/buildrpm-cron <<EOF
#!/bin/sh

ARCH=%{_target_cpu}
EOF
cat $RPM_BUILD_ROOT/home/users/builder/bin/buildrpm-cron.bak >> $RPM_BUILD_ROOT/home/users/builder/bin/buildrpm-cron
rm -f $RPM_BUILD_ROOT/home/users/builder/bin/buildrpm-cron.bak

install cron/builder $RPM_BUILD_ROOT/etc/cron.d/

%pre
if [ "$1" = "1" ]; then
	if [ ! -n "`id -u builder 2>/dev/null`" ]; then
		%{_sbindir}/useradd -g users -d /home/users/builder -m -s /bin/bash builder 2> /dev/null
	fi
fi

%postun
if [ "$1" = "0" ]; then
	%{_sbindir}/userdel builder 2> /dev/null
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(600,builder,builder,700)
%attr(640,root,root) /etc/cron.d/builder
%dir /home/users/builder
%dir /home/users/builder/.requests-%{_target_cpu}
%dir /home/users/builder/bin
%dir /home/users/builder/chroot-%{_target_cpu}
%dir /home/users/builder/chroot-%{_target_cpu}/home/users/builder
%dir /home/users/builder/chroot-%{_target_cpu}/home/users/builder/bin
%config(noreplace) %verify(not size mtime md5) /home/users/builder/.builderrc
%config(noreplace) %verify(not size mtime md5) /home/users/builder/.procmailrc
%config(noreplace) %verify(not size mtime md5) /home/users/builder/chroot-%{_target_cpu}/home/users/builder/.builderrc
%config(noreplace) %verify(not size mtime md5) /home/users/builder/chroot-%{_target_cpu}/home/users/builder/.rpm*
%attr(700,builder,builder) %config(noreplace) %verify(not size mtime md5) /home/users/builder/bin/*
%attr(700,builder,builder) %config(noreplace) %verify(not size mtime md5) /home/users/builder/chroot-%{_target_cpu}/home/users/builder/bin/*
