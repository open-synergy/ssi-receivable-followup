import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-open-synergy-ssi-receivable-followup",
    description="Meta package for open-synergy-ssi-receivable-followup Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ssi_receivable_follow_up',
        'odoo14-addon-ssi_receivable_follow_up_operating_unit',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
