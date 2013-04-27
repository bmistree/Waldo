
import waldoReferenceValue
import waldoReferenceBase

from waldoReferenceContainerBase import _ReferenceContainerVersion as RefContainerVers



def deserialize_version_obj_from_network_data(version_network_data):
    '''
    @param {Currently string} version_network_data --- The result
    of a call to serilizable_for_network_data on a version object.
    '''

    if (version_network_data[0] ==
        waldoReferenceBase._ReferenceVersion.REFERENCE_VALUE_VERSION):

        return waldoReferenceValue._ReferenceValueVersion.deserialize_version_obj_from_network_data(
            version_network_data)

    elif (version_network_data[0] ==
          waldoReferenceBase._ReferenceVersion.REFERENCE_CONTAINER_VERSION):

        return RefContainerVers.deserialize_version_obj_from_network_data(
            version_network_data)
