
def with_field(self, submodel_name: str, field_name: str, field_value: object):
    submodel = getattr(self, submodel_name)
    
    new_submodel_dict = self.submodel.model_dump() | {field_name: field_value}
    new_submodel = type(submodel)(**new_submodel_dict)
    
    return self.model_copy(update={submodel_name: new_submodel})
