import json
import re

# Let's map the user's 26 Excel values:
excel_user_list = [
    ("Subscription (Min 200.00)", 205700),
    ("Donation General", 272080),
    ("Catholicate Day & Recessa", 36050),
    ("Metropolitan Fund", 16450),
    ("Mission Sunday", 10550),
    ("Seminary Day", 7450),
    ("Priest Welfare Fund", 8200),
    ("Old Cover Collection Dues", 8100),
    ("Wedding Anniversary Offerings", 9500),
    ("Birthday Offerings", 22750),
    ("Baptism", 2500),
    ("Orma Qurbana/Holy Qurbana", 7220),
    ("Sunday School Day Collection", 5650),
    ("St. Gregorios Feast", 1600),
    ("Parish Day/Harvest", 1500),
    ("Parish Vanchika (House Offertory)", 5800),
    ("Pension Scheme Collection / Passion Week", 78606),
    ("St. George Feast", 15500),
    ("St. Thomas Feast", 600),
    ("St. Mary's Feast", 85300),
    ("Harvest Festival", 1500),
    ("Passion Week Collection", 1500),
    ("Charity Fund", 1000),
    ("Building Fund", 96500),
    ("Others", 156300),
]

# Let's check the sum of the Excel values:
items_text = [205700, 272080, 36050, 16450, 10550, 7450, 8200, 8100, 9500, 22750, 2500, 7220, 5650, 1600, 1500, 5800, 78606, 15500, 600, 85300, 1500, 1500, 1000, 96500, 156300]
print("Sum of individual values in user text:", sum(items_text))
print("User text claimed GRAND TOTAL:", 1057906)
print("Difference between sum of columns and user claimed GRAND TOTAL in text:", 1057906 - sum(items_text))

# Now let's check the image Excel row values:
items_image = [205700, 272080, 36050, 16450, 10550, 7450, 8200, 8100, 9500, 22750, 2500, 7220, 5650, 5800, 78606, 15500, 600, 85300, 1500, 1500, 1000, 96500, 156300]
print("\nSum of individual values in Excel image:", sum(items_image))
print("Excel image claimed GRAND TOTAL:", 1056306)
print("Difference between sum of columns and Excel image claimed GRAND TOTAL:", 1056306 - sum(items_image))

