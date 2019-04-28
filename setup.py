from numpy.distutils.core import setup


setup(name='waspy',
    version='0.0.1',
    description='Wing Aerostructural Studies in Python',
    author='John Jasa',
    author_email='johnjasa@umich.edu',
    license='BSD-3',
    packages=[
        'waspy',
        'waspy/CRM',
    ],
    install_requires=[],
    zip_safe=False,
    # ext_modules=ext,
)
