DESIGNERDIR = ./designer_files
UIPYTHONDIR = ./python_package/ui
PKPYTHONDIR = ./python_package
RESOURCES = parkmanager.qrc

RM = /bin/rm
PYRCC = /usr/bin/pyrcc5
PYUIC = /usr/bin/pyuic5
IMPORTRM = ./python_package/utils/remove_import.py

UIFILES := $(wildcard $(DESIGNERDIR)/*.ui)

PYTHONUI = $(addprefix $(UIPYTHONDIR)/,$(notdir $(UIFILES:%.ui=%.py)))
PYTHONRC = $(RESOURCES:%.qrc=$(UIPYTHONDIR)/%_rc.py)
PYTHONUIPYC = $(UIPYTHONDIR)/__pycache__
PYTHONPKPYC = $(PKPYTHONDIR)/__pycache__

all: resources ui

resources: $(PYTHONRC)

ui: $(PYTHONUI)

$(UIPYTHONDIR)/%.py: $(DESIGNERDIR)/%.ui
	$(PYUIC) -o $@ $<
	$(IMPORTRM) $@

$(UIPYTHONDIR)/%_rc.py: $(RESOURCES)
	$(PYRCC) -o $@ $<

clean:
	$(RM) $(PYTHONUI) $(PYTHONRC)
	$(RM) -r $(PYTHONUIPYC) $(PYTHONPKPYC)
