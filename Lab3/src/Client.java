import java.io.*;
import java.net.*;

public class Client {
    private Socket socket   =null;
    private DataInputStream input = null;
    private DataOutputStream out = null;

    // to put ip address
    public Client(String address, int port){
        try
        {
            socket = new Socket(address, port);//
            System.out.println("Connected");
            // take input from terminal
            input = new DataInputStream(System.in);
            // send output via the socket
            out = new DataOutputStream(socket.getOutputStream());

        }
        catch(UnknownHostException u)
        {
            System.out.println(u);

        }
        catch(IOException i)
        {
            System.out.println(i);
        }
        // string to read message from input
        String line="";


        // keep reading until over
        while(!line.equals("Over"))
        {
            try{
                line = input.readLine();
                out.writeUTF(line);
            }
            catch(IOException i){
                System.out.println(i);
            }
        }
        // close the connection
        try{
            input.close();
            out.close();
            socket.close();
        }
        catch(IOException i) {
            System.out.println(i);
        }

    }
    public static void main(String args[])
    {
        Client client = new Client("127.0.0.1", 5000);
    }
}
