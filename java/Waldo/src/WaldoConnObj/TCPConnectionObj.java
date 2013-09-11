package WaldoConnObj;


import java.io.IOException;

import waldo.Endpoint;
import waldo_protobuffs.GeneralMessageProto.GeneralMessage;

public class TCPConnectionObj implements ConnectionObj, Runnable
{
	private Endpoint local_endpoint = null;
	private java.net.Socket sock = null;
	
	/**
	 * If not passed in a socket, then
        create a new connection to dst_host, dst_port.
        Use sock for this connection.
	 * @throws IOException 

	 */
	public TCPConnectionObj(String dst_host, int dst_port) throws IOException
	{

		sock = new java.net.Socket(dst_host,dst_port);
		sock.setTcpNoDelay(true);
	}

	public TCPConnectionObj(java.net.Socket _sock) 
	{
		sock = _sock;
	}
	
	/**
	 * Actually close the socket
	 * @throws IOException 
	 */
	public void close() 
	{
		try {
			sock.close();
		} catch (IOException e) {
			local_endpoint.partner_connection_failure();
		}
	}

    public void write_stop(GeneralMessage msg_to_write,waldo.Endpoint endpoint_writing)
    {
    	write(msg_to_write,endpoint_writing);
    }
     
    

    /**
        @param {String} msg_str_to_write
        @param {Endpoint} sender_endpoint_obj
        
        Gets called from endpoint to send message from one side to the
        other.
     */    
	public void write(GeneralMessage msg_to_write, waldo.Endpoint sender_endpoint_obj)
	{
		try {
			msg_to_write.writeDelimitedTo(sock.getOutputStream());
		} catch (IOException e) {
			local_endpoint.partner_connection_failure();			
		}
	}

	/**
        @param {_Endpoint object} local_endpoint --- @see the emitted
        code for a list of _Endpoint object methods.
        
        Once we have an attached endpoint, we start listening for data
        to send to that endpoint.
	 */
	public void register_endpoint(waldo.Endpoint _local_endpoint)
	{
        local_endpoint = _local_endpoint;
        
        // create anonymous thread to start listening on the connection:
        Thread t = new Thread(this);
        t.setDaemon(true);
        t.start();
	}

	public void run ()
	{
		listening_loop();
	}

	private void listening_loop()
	{
		while (true)
		{
			GeneralMessage gm = null;
			try {
				gm = GeneralMessage.parseDelimitedFrom(sock.getInputStream());
			} catch (IOException e) {
				local_endpoint.partner_connection_failure();
				break;
			}
			local_endpoint._receive_msg_from_partner(gm);			
		}
	}
	
}


