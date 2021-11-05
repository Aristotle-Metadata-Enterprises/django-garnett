from garnett.fields import TranslatedField


def patch_compare():
    from reversion_compare.compare import CompareObjects as COBase

    class CompareObjects(COBase):
        def __init__(self, field, field_name, obj, version1, version2, is_reversed):
            if isinstance(field, TranslatedField):
                field_name = field.attname
            super().__init__(field, field_name, obj, version1, version2, is_reversed)

    # Import this as late as possible as we are monkey patching over it
    import reversion_compare.compare

    reversion_compare.compare.CompareObjects = CompareObjects
