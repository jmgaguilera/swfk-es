#coding=utf-8
from distutils.core import setup, Command
from distutils.spawn import find_executable, spawn
from zipfile import ZipFile

import os
import re


#
# where to write target files
#
target_dir = 'target'

#
# 
#
platforms = 'win', 'mac', 'linux'
#platforms = 'win',

#
# find the executables to use in compiling the books
#
latex = find_executable('latex')
makeindex = find_executable('makeindex')
dvipdf = find_executable('dvipdf')

#
# Get the book version
#
s = open('frontmatter.tex').read()
mat = re.compile(r'Versión\s*(.*)').findall(s)
version = mat[1]
versionPDF = version

if not os.path.exists(target_dir):
    os.mkdir(target_dir)

class CleanCommand(Command):
    user_options = [ ]

    def initialize_options(self):
        self._clean_me = [ ]
        for root, dirs, files in os.walk(target_dir):
            for f in files:
                self._clean_me.append(os.path.join(root, f))

    def finalize_options(self):
        pass

    def run(self):
        for clean_me in self._clean_me:
            try:
                os.unlink(clean_me)
            except:
                pass


class LatexCommand(Command):
    user_options = [ ('cover=', 'c', 'include the cover in the output') ]

    def initialize_options(self):
        self.cover = 'include'

    def finalize_options(self):
        pass

    def run(self):
        for platform in platforms:
            s = open('swfk.tex.pre').read()
            if self.cover == 'include':
                s = s.replace('@FRONTCOVER_INC@', 'include')
                fname_suffix = ''
            else:
                s = s.replace('@FRONTCOVER_INC@', 'exclude')
                fname_suffix = '-nc'
                
            if platform == 'win':
                s = s.replace('@WINDOWS_INC@', 'include')
                s = s.replace('@MAC_INC@', 'exclude')
                s = s.replace('@LINUX_INC@', 'exclude')
            elif platform == 'mac':
                s = s.replace('@WINDOWS_INC@', 'exclude')
                s = s.replace('@MAC_INC@', 'include')
                s = s.replace('@LINUX_INC@', 'exclude')
            elif platform == 'linux':
                s = s.replace('@WINDOWS_INC@', 'exclude')
                s = s.replace('@MAC_INC@', 'exclude')
                s = s.replace('@LINUX_INC@', 'include')
            else:
                raise RuntimeError('unrecognised platform %s' % platform)

            swfk_tex = open('swfk.tex', 'w')
            swfk_tex.write(s)
            swfk_tex.close()
        
            tex = 'swfk.tex'
            try:
                spawn([latex, '--output-directory=%s' % target_dir, tex])
            except:
                pass
            spawn([makeindex, '%s/swfk.idx' % target_dir])
            try:
               spawn([latex, '--output-directory=%s' % target_dir, tex])
            except:
                pass

            pdf = '%s/swfk-es-%s-%s%s.pdf' % (target_dir, platform, version, fname_suffix)
            spawn([dvipdf, '%s/swfk.dvi' % target_dir, pdf])

            zf = ZipFile('%s/swfk-es-%s-%s%s.zip' % (target_dir, platform, version, fname_suffix), 'w')
            zf.write(pdf)
            zf.close()


setup(
    name = 'SWFK-ES',
    version = versionPDF,
    description = 'Doma de Serpientes Para Niños',

    author = 'José Miguel González Aguilera',
    author_email =  'jmgaguilera@gmail.com',

    cmdclass = { 'clean': CleanCommand, 'build' : LatexCommand }

)
