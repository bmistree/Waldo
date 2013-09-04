package waldo;

import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleNumberDelta;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleTextDelta;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleTrueFalseDelta;

public class LockedVariables {
	final static ValueTypeDataWrapperConstructor<Number> number_value_type_data_wrapper_constructor = new ValueTypeDataWrapperConstructor<Number>();
	final static Number default_number = new Double(0);

	final static ValueTypeDataWrapperConstructor<String> text_value_type_data_wrapper_constructor = new ValueTypeDataWrapperConstructor<String>();
	final static String default_text = new String();
	
	final static ValueTypeDataWrapperConstructor<Boolean> true_false_value_type_data_wrapper_constructor = 
			new ValueTypeDataWrapperConstructor<Boolean>();
	final static Boolean default_tf = false;
	
	
	
	public static class SingleThreadedLockedNumberVariable extends SingleThreadedLockedValueVariable<Number>
	{
		public SingleThreadedLockedNumberVariable(String _host_uuid, boolean _peered,
			Number init_val)
		{
			super(_host_uuid,_peered,init_val,default_number,number_value_type_data_wrapper_constructor);
			
		}

		
		@Override
		protected boolean value_variable_py_val_serialize(
				waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.Builder parent_delta,
				Number var_data, String var_name) 
		{
			// can only add a pure number to var store a holder or to
	        // an added key
			SingleNumberDelta.Builder delta = SingleNumberDelta.newBuilder();
			delta.setVarName(var_name);
			delta.setVarData(var_data.doubleValue());
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

	public static class SingleThreadedLockedTextVariable extends SingleThreadedLockedValueVariable<String>
	{
		public SingleThreadedLockedTextVariable(String _host_uuid, boolean _peered,
			String init_val)
		{
			super(_host_uuid,_peered,init_val,default_text,text_value_type_data_wrapper_constructor);
		}
		
		@Override
		protected boolean value_variable_py_val_serialize(
				waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.Builder parent_delta,
				String var_data, String var_name) 
		{
			// can only add a pure number to var store a holder or to
	        // an added key
			SingleTextDelta.Builder delta = SingleTextDelta.newBuilder();
			delta.setVarName(var_name);
			delta.setVarData(var_data);
			parent_delta.addTextDeltas(delta);			
			return true;
		}

		@Override
		protected boolean value_variable_py_val_serialize(
				waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerAddedKey.Builder parent_delta,
				String var_data, String var_name) 
		{
			parent_delta.setAddedWhatText(var_data);
            return true;
		}

		@Override
		protected boolean value_variable_py_val_serialize(
				waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerWriteKey.Builder parent_delta,
				String var_data, String var_name) 
		{
			parent_delta.setWhatWrittenText(var_data);
			return true;
		}
		
	}

	public static class SingleThreadedLockedTrueFalseVariable extends SingleThreadedLockedValueVariable<Boolean>
	{
		public SingleThreadedLockedTrueFalseVariable(String _host_uuid, boolean _peered,
			Boolean init_val)
		{
			super(_host_uuid,_peered,init_val,default_tf,true_false_value_type_data_wrapper_constructor);
		}
		
		@Override
		protected boolean value_variable_py_val_serialize(
				waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.Builder parent_delta,
				Boolean var_data, String var_name) 
		{
			// can only add a pure number to var store a holder or to
	        // an added key
			SingleTrueFalseDelta.Builder delta = SingleTrueFalseDelta.newBuilder();
			delta.setVarName(var_name);
			delta.setVarData(var_data);
			parent_delta.addTrueFalseDeltas(delta);			
			return true;
		}

		@Override
		protected boolean value_variable_py_val_serialize(
				waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerAddedKey.Builder parent_delta,
				Boolean var_data, String var_name) 
		{
			parent_delta.setAddedWhatTf(var_data);
            return true;
		}

		@Override
		protected boolean value_variable_py_val_serialize(
				waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerWriteKey.Builder parent_delta,
				Boolean var_data, String var_name) 
		{
			parent_delta.setWhatWrittenTf(var_data);
			return true;
		}
		
	}

	
	
}
