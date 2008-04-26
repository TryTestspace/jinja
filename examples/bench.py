"""
    This benchmark compares some python templating engines with Jinja 2 so
    that we get a picture of how fast Jinja 2 is for a semi real world
    template.  If a template engine is not installed the test is skipped.
"""
import sys
from timeit import Timer
from jinja2 import Environment as JinjaEnvironment

context = {
    'page_title': 'mitsuhiko\'s benchmark',
    'table': [dict(a=1,b=2,c=3,d=4,e=5,f=6,g=7,h=8,i=9,j=10) for x in range(1000)]
}

jinja_template = JinjaEnvironment(
    line_statement_prefix='%',
    variable_start_string="${",
    variable_end_string="}"
).from_string("""\
<!doctype html>
<html>
  <head>
    <title>${page_title|e}</title>
  </head>
  <body>
    <div class="header">
      <h1>${page_title|e}</h1>
    </div>
    <ul class="navigation">
    % for href, caption in [
        ('index.html', 'Index'),
        ('downloads.html', 'Downloads'),
        ('products.html', 'Products')
      ]
      <li><a href="${href|e}">${caption|e}</a></li>
    % endfor
    </ul>
    <div class="table">
      <table>
      % for row in table
        <tr>
        % for cell in row
          <td>${cell}</td>
        % endfor
        </tr>
      % endfor
      </table>
    </div>
  </body>
</html>\
""")

def test_jinja():
    jinja_template.render(context)

try:
    from django.conf import settings
    settings.configure()
    from django.template import Template as DjangoTemplate, Context as DjangoContext
except ImportError:
    test_django = None
else:
    django_template = DjangoTemplate("""\
<!doctype html>
<html>
  <head>
    <title>{{ page_title }}</title>
  </head>
  <body>
    <div class="header">
      <h1>{{ page_title }}</h1>
    </div>
    <ul class="navigation">
    {% for href, caption in navigation %}
      <li><a href="{{ href }}">{{ caption }}</a></li>
    {% endfor %}
    </ul>
    <div class="table">
      <table>
      {% for row in table %}
        <tr>
        {% for cell in row %}
          <td>{{ cell }}</td>
        {% endfor %}
        </tr>
      {% endfor %}
      </table>
    </div>
  </body>
</html>\
""")

    def test_django():
        c = DjangoContext(context)
        c['navigation'] = [('index.html', 'Index'), ('downloads.html', 'Downloads'),
                           ('products.html', 'Products')]
        django_template.render(c)

try:
    from mako.template import Template as MakoTemplate
except ImportError:
    test_mako = None
else:
    mako_template = MakoTemplate("""\
<!doctype html>
<html>
  <head>
    <title>${page_title|h}</title>
  </head>
  <body>
    <div class="header">
      <h1>${page_title|h}</h1>
    </div>
    <ul class="navigation">
    % for href, caption in [('index.html', 'Index'), ('downloads.html', 'Downloads'), ('products.html', 'Products')]:
      <li><a href="${href|h}">${caption|h}</a></li>
    % endfor
    </ul>
    <div class="table">
      <table>
      % for row in table:
        <tr>
        % for cell in row:
          <td>${cell}</td>
        % endfor
        </tr>
      % endfor
      </table>
    </div>
  </body>
</html>\
""")

    def test_mako():
        mako_template.render(**context)

try:
    from genshi.template import MarkupTemplate as GenshiTemplate
except ImportError:
    test_genshi = None
else:
    genshi_template = GenshiTemplate("""\
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/">
  <head>
    <title>${page_title}</title>
  </head>
  <body>
    <div class="header">
      <h1>${page_title}</h1>
    </div>
    <ul class="navigation">
      <li py:for="href, caption in [
        ('index.html', 'Index'),
        ('downloads.html', 'Downloads'),
        ('products.html', 'Products')]"><a href="${href}">${caption}</a></li>
    </ul>
    <div class="table">
      <table>
        <tr py:for="row in table">
          <td py:for="cell in row">${cell}</td>
        </tr>
      </table>
    </div>
  </body>
</html>\
""")

    def test_genshi():
        genshi_template.generate(**context).render('html', strip_whitespace=False)

try:
    from Cheetah.Template import Template as CheetahTemplate
except ImportError:
    test_cheetah = None
else:
    cheetah_template = CheetahTemplate("""\
#import cgi
<!doctype html>
<html>
  <head>
    <title>$cgi.escape($page_title)</title>
  </head>
  <body>
    <div class="header">
      <h1>$cgi.escape($page_title)</h1>
    </div>
    <ul class="navigation">
    #for $href, $caption in [('index.html', 'Index'), ('downloads.html', 'Downloads'), ('products.html', 'Products')]:
      <li><a href="$cgi.escape($href)">$cgi.escape($caption)</a></li>
    #end for
    </ul>
    <div class="table">
      <table>
      #for $row in $table:
        <tr>
        #for $cell in $row:
          <td>$cell</td>
        #end for
        </tr>
      #end for
      </table>
    </div>
  </body>
</html>\
""", searchList=[dict(context)])

    def test_cheetah():
        unicode(cheetah_template)

try:
    import tenjin
except ImportError:
    test_tenjin = None
else:
    tenjin_template = tenjin.Template()
    tenjin_template.convert("""\
<!doctype html>
<html>
  <head>
    <title>${page_title}</title>
  </head>
  <body>
    <div class="header">
      <h1>${page_title}</h1>
    </div>
    <ul class="navigation">
<?py for href, caption in [('index.html', 'Index'), ('downloads.html', 'Downloads'), ('products.html', 'Products')]: ?>
      <li><a href="${href}">${caption}</a></li>
<?py #end ?>
    </ul>
    <div class="table">
      <table>
<?py for row in table: ?>
        <tr>
<?py     for cell in row: ?>
          <td>#{cell}</td>
<?py #end ?>
        </tr>
<?py #end ?>
      </table>
    </div>
  </body>
</html>\
""")

    def test_tenjin():
        from tenjin.helpers import escape, to_str
        tenjin_template.render(context, locals())

sys.stdout.write('\r' + '\n'.join((
    '=' * 80,
    'Template Engine BigTable Benchmark'.center(80),
    '-' * 80,
    __doc__,
    '-' * 80
)) + '\n')
for test in 'jinja', 'tenjin', 'mako', 'django', 'genshi', 'cheetah':
    if locals()['test_' + test] is None:
        sys.stdout.write('  %-20s*not installed*\n' % test)
        continue
    t = Timer(setup='from __main__ import test_%s as bench' % test,
              stmt='bench()')
    sys.stdout.write('> %-20s<running>' % test)
    sys.stdout.flush()
    sys.stdout.write('\r  %-20s%.4f ms\n' % (test, t.timeit(number=20) / 20))
sys.stdout.write('=' * 80 + '\n')
