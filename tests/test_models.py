# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should read a product from the database"""
        product = ProductFactory()
        print(product)
        app.logger.info("Product %s", product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        db_product = Product.find(product.id)
        self.assertEqual(product.id, db_product.id)
        self.assertEqual(product.name, db_product.name)
        self.assertEqual(product.description, db_product.description)
        self.assertEqual(product.price, db_product.price)
        self.assertEqual(product.available, db_product.available)
        self.assertEqual(product.category, db_product.category)

    def test_update_a_product(self):
        """It should update a product in the database"""
        product = ProductFactory()
        app.logger.info("Product %s", product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        app.logger.info("Product %s", product)
        product.description = "DEFINITELY BETTER PRODUCT"
        original_id = product.id
        product.update()
        self.assertEqual(original_id, product.id)
        self.assertEqual(product.description, "DEFINITELY BETTER PRODUCT")
        results = Product.all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, original_id)
        self.assertEqual(results[0].description, "DEFINITELY BETTER PRODUCT")

    def test_update_a_product_missing_id(self):
        """It should raise the exception if id is None"""
        product = ProductFactory()
        app.logger.info("Product %s", product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product.id = None
        app.logger.info("Product %s", product)
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should Delete a Product from the database"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should list all products in the database"""
        products = Product.all()
        self.assertEqual(len(products), 0)
        for _ in range(5):
            product = ProductFactory()
            product.create()
        self.assertEqual(len(Product.all()), 5)

    def test_find_by_name(self):
        """It should find products in the database by name"""
        products = ProductFactory.create_batch(5)
        for i in range(5):
            products[i].create()
        first_product = products[0]
        count = len([product for product in products if product.name == first_product.name])
        found = Product.find_by_name(first_product.name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, first_product.name)

    def test_find_by_availability(self):
        """It should find products in the database by availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        first_avail = products[0].available
        count = len([product for product in products if product.available == first_avail])
        found = Product.find_by_availability(first_avail)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, first_avail)

    def test_find_by_category(self):
        """It should find products in the database by category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        first_category = products[0].category
        count = len([product for product in products if product.category == first_category])
        found = Product.find_by_category(first_category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, first_category)
