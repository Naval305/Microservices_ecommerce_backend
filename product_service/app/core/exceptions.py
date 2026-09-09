class ParentCategoryNotFoundError(Exception):
    pass


class CategoryExistsError(Exception):
    pass


class CategoryNotExistsError(Exception):
    pass


class SameCategoryParentError(Exception):
    pass


class ProductExistsError(Exception):
    pass


class ProductNotExistsError(Exception):
    pass
