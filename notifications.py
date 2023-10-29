from helper_funcs import id_to_link

def notify(property_dict):
    assert 'Notified' in property_dict.keys()
    print(f'Notifying for {id_to_link(property_dict["id"])}')
    print(property_dict)

    # TODO: check that this is getting saved, should do if it's being called using with open...
    property_dict['Notified'] == True