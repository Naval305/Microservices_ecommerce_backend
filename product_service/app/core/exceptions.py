class ParentCategoryNotFoundError(Exception):
    pass


class CategoryExistsError(Exception):
    pass


class CategoryNotExistsError(Exception):
    pass


class SameCategoryParentError(Exception):
    pass