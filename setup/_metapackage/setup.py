import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-open-synergy-ssi-receivable-followup",
    description="Meta package for open-synergy-ssi-receivable-followup Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-ssi_receivable_follow_up',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 11.0',
    ]
)
