from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Iterable

from products import Product, ProductFactory


class ProductGroup:
    """A collection of like products that can be driven concurrently."""

    def __init__(self, name: str, products: Iterable[Product]):
        self.name = name
        self.products = list(products)

    def __len__(self) -> int:
        return len(self.products)

    def __iter__(self):
        return iter(self.products)

    def __getitem__(self, index: int) -> Product:
        return self.products[index]

    def open(self, page_name: str) -> "ProductGroup":
        self._concurrently(lambda product: product.open(page_name))
        return self

    def click(self, element_name: str) -> "ProductGroup":
        self._concurrently(lambda product: product.click(element_name))
        return self

    def call(self, method_name: str, *args, **kwargs) -> list[Any]:
        return self._concurrently(
            lambda product: getattr(product, method_name)(*args, **kwargs)
        )

    def _concurrently(self, operation: Callable[[Product], Any]) -> list[Any]:
        if not self.products:
            return []
        with ThreadPoolExecutor(max_workers=len(self.products)) as executor:
            return list(executor.map(operation, self.products))


class System:
    def __init__(self, product_groups: dict[str, ProductGroup]):
        self.product_groups = product_groups

    def product(self, name: str) -> ProductGroup:
        if name not in self.product_groups:
            available = ", ".join(sorted(self.product_groups)) or "none"
            raise KeyError(f"Unknown product group '{name}'. Available groups: {available}")
        return self.product_groups[name]

    def __getattr__(self, name: str) -> ProductGroup:
        try:
            return self.product(name)
        except KeyError as error:
            raise AttributeError(str(error)) from error

    def quit(self) -> None:
        for group in self.product_groups.values():
            for product in group:
                product.quit()


class SystemFactory:
    @staticmethod
    def create(
        product_configs: dict[str, list[dict[str, Any]]],
        driver_factory: Callable[[str, int, dict[str, Any]], Any] | None = None,
    ) -> System:
        groups = {}
        for group_name, configs in product_configs.items():
            products = []
            for index, config in enumerate(configs):
                driver = None
                if config.get("ui"):
                    if driver_factory is None:
                        raise ValueError(
                            f"UI product '{group_name}' requires a driver_factory"
                        )
                    driver = driver_factory(group_name, index, config)
                products.append(ProductFactory.create(driver=driver, config=config))
            groups[group_name] = ProductGroup(group_name, products)
        return System(groups)
