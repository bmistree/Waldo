package waldo;

import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleNumberDelta;

public class LockedVariables {
	final static ValueTypeDataWrapperConstructor<Number> number_value_type_data_wrapper_constructor = new ValueTypeDataWrapperConstructor<Number>();
	final static Number default_number = new Double(0);
	
	public static class SingleThreadedLockedNumberVariable extends SingleThreadedLockedValueVariable<Number>
	{
		public SingleThreadedLockedNumberVariable(String _host_uuid, boolean _peered,
			Number init_val)
		{
			super(_host_uuid,_peered,init_val,default_number,number_value_type_data_wrapper_constructor);
			
		}

		
		@Override
		protected boolean value_variable_py_val_serialize(VarStoreDeltas.Builder parent_delta,
				Number var_data, String var_name) 
		{
			// can only add a pure number to var store a holder or to
	        // an added key
			SingleNumberDelta.Builder delta = SingleNumberDelta.newBuilder();
			parent_delta.addNumDeltas(delta);			
			return true;
		}

		@Override
		protected boolean value_variable_py_val_serialize(
				waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerAddedKey.Builder parent_delta,
				Number var_data, String var_name) 
		{
			//parent_delta.added_what_num = var_data
			parent_delta.setAddedWhatNum(var_data.doubleValue());
            return true;
		}

		@Override
		protected boolean value_variable_py_val_serialize(
				waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerWriteKey.Builder parent_delta,
				Number var_data, String var_name) 
		{
			// parent.what_written_num = var_data
			parent_delta.setWhatWrittenNum(var_data.doubleValue());
			return true;
		}
		
	}

}
