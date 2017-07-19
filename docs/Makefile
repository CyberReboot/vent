# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
GH_PAGES_SOURCES  = source 
SPHINXOPTS    	  = 
SPHINXBUILD   	  = python -msphinx
SPHINXPROJ    	  = Vent
SOURCEDIR      	  = source
BUILDDIR      	  = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

gh-pages:
	git checkout gh-pages
	rm -rf build _sources _static
	git checkout master $(GH_PAGES_SOURCES)
	git reset HEAD
	make html
	mv -fv build/html/* ./
	rm -rf $(GH_PAGES_SOURCES) build
	git add -A
	git ci -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`" && git push origin gh-pages ; git checkout master

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
