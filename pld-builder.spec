Summary:	PLD rpm builder environment
Summary(pl):	¦rodowisko budowniczego pakietów dla PLD
Name:		pld-builder
Version:	1.2
Release:	2
License:	GPL
Group:		Development/Building
Source0:	%{name}-%{version}.tar.gz
# Source0-md5:	52bf879d996eb235173558bf32e20a8f
Patch0:		%{name}-athlon.patch
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

%define _builderdir /home/users/builder

%description
PLD rpm builder environment.

%description -l pl
¦rodowisko budowniczego pakietów dla PLD.

%prep
%setup -q
%patch0 -p1

%build
echo "ARCH=%{_target_cpu}" >> .builderrc
echo "ARCH=%{_target_cpu}" >> chroot/.builderrc

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_builderdir}/{.requests-%{_target_cpu},bin,Attic} \
	$RPM_BUILD_ROOT%{_builderdir}/chroot-%{_target_cpu}/home/users/builder/bin \
	$RPM_BUILD_ROOT/etc/cron.d

install .builderrc $RPM_BUILD_ROOT%{_builderdir}
install .procmailrc $RPM_BUILD_ROOT%{_builderdir}
install bin/* $RPM_BUILD_ROOT%{_builderdir}/bin

install chroot/.builderrc $RPM_BUILD_ROOT%{_builderdir}/chroot-%{_target_cpu}/home/users/builder
install chroot/.rpmmacros $RPM_BUILD_ROOT%{_builderdir}/chroot-%{_target_cpu}/home/users/builder
%ifarch %{ix86}
install chroot/.rpmrc.%{_target_cpu} $RPM_BUILD_ROOT%{_builderdir}/chroot-%{_target_cpu}/home/users/builder/.rpmrc
%endif
install chroot/bin/* $RPM_BUILD_ROOT%{_builderdir}/chroot-%{_target_cpu}/home/users/builder/bin

mv -f $RPM_BUILD_ROOT%{_builderdir}/bin/buildrpm-cron $RPM_BUILD_ROOT%{_builderdir}/bin/buildrpm-cron.bak
cat > $RPM_BUILD_ROOT%{_builderdir}/bin/buildrpm-cron <<EOF
#!/bin/sh

ARCH=%{_target_cpu}
EOF
cat $RPM_BUILD_ROOT%{_builderdir}/bin/buildrpm-cron.bak >> $RPM_BUILD_ROOT%{_builderdir}/bin/buildrpm-cron
rm -f $RPM_BUILD_ROOT%{_builderdir}/bin/buildrpm-cron.bak

install cron/builder $RPM_BUILD_ROOT/etc/cron.d

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ "$1" = "1" ]; then
	if [ ! -n "`id -u builder 2>/dev/null`" ]; then
		/usr/sbin/useradd -g users -d %{_builderdir} -m -s /bin/bash builder 2> /dev/null
	fi
fi

%postun
if [ "$1" = "0" ]; then
	/usr/sbin/userdel builder 2> /dev/null
fi

%files
%defattr(644,root,root,755)
%attr(640,root,root) /etc/cron.d/builder
%dir %{_builderdir}
%dir %{_builderdir}/.requests-%{_target_cpu}
%dir %{_builderdir}/bin
%dir %{_builderdir}/chroot-%{_target_cpu}
%dir %{_builderdir}/chroot-%{_target_cpu}/home/users/builder
%dir %{_builderdir}/chroot-%{_target_cpu}/home/users/builder/bin
%config(noreplace) %verify(not size mtime md5) %{_builderdir}/.builderrc
%config(noreplace) %verify(not size mtime md5) %{_builderdir}/.procmailrc
%config(noreplace) %verify(not size mtime md5) %{_builderdir}/chroot-%{_target_cpu}/home/users/builder/.builderrc
%config(noreplace) %verify(not size mtime md5) %{_builderdir}/chroot-%{_target_cpu}/home/users/builder/.rpm*
%attr(700,builder,root) %config(noreplace) %verify(not size mtime md5) %{_builderdir}/bin/*
%attr(700,builder,root) %config(noreplace) %verify(not size mtime md5) %{_builderdir}/chroot-%{_target_cpu}/home/users/builder/bin/*
