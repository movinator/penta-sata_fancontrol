SM = /usr/sbin/smartctl
TL = /usr/sbin/TempLogger
ifeq ($(shell test -e $(SM) && echo -n yes), yes)
		SMI = ok
else
		SMI = false
endif
ifeq ($(shell test -e $(TL) && echo -n yes), yes)
		TLI = ok
else
		TLI = false
endif


install:
ifeq ($(TLI), ok)
	install sources/etc/rockpi-sata.conf /etc
	install sources/usr/sbin/fanctl /usr/sbin
	install sources/usr/lib/python3/dist-packages/* /usr/lib/python3/dist-packages
	install sources/usr/lib/systemd/system/fanctl.service /usr/lib/systemd/system
	systemctl enable fanctl.service
	systemctl start fanctl.service
else
ifeq ($(SMI), ok)
	install sources/etc/rockpi-sata.conf /etc
	install sources/usr/sbin/fanctl /usr/sbin
	install sources/usr/lib/python3/dist-packages/* /usr/lib/python3/dist-packages
	install sources/usr/lib/systemd/system/fanctl.service /usr/lib/systemd/system
	systemctl enable fanctl.service
	systemctl start fanctl.service
else
		@echo fanctl requires TempLogger or smartctl. Please install one of them.
endif
endif
