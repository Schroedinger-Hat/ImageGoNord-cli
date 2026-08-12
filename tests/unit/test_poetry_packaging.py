import tomllib
from pathlib import Path
from unittest import TestCase


class PoetryPackagingShould(TestCase):
    def setUp(self):
        self.pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
        self.pyproject = tomllib.loads(self.pyproject_path.read_text(encoding="utf-8"))

    def test_define_poetry_metadata(self):
        poetry = self.pyproject["tool"]["poetry"]
        self.assertEqual("image-go-nord-client", poetry["name"])
        self.assertEqual("1.0.0", poetry["version"])

    def test_define_console_scripts(self):
        scripts = self.pyproject["tool"]["poetry"]["scripts"]
        self.assertEqual("image_go_nord_client.main:main", scripts["image-go-nord-client"])
        self.assertEqual("image_go_nord_client.ign:run", scripts["ign"])

    def test_include_palette_and_version_package_data(self):
        include = self.pyproject["tool"]["poetry"]["include"]
        self.assertIn("src/image_go_nord_client/VERSION", include)
        self.assertIn("src/image_go_nord_client/palettes/**/*.txt", include)

    def test_include_textual_dependency(self):
        dependencies = self.pyproject["tool"]["poetry"]["dependencies"]
        self.assertIn("textual", dependencies)
