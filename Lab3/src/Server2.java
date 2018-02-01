import java.net.*;
import java.io.*;

public class Server2 {
    private Socket socket   =null;
    private ServerSocket server = null;
    private DataInputStream in = null;
    private int port;
    public Server2(int port){
        // starts the server and waits for a connection
        try{
            this.port = port;
            server = new ServerSocket(port);
            System.out.println("Server started: ");
            System.out.println("Waiting for a client");
            socket = server.accept();
            System.out.println("Client accepted");

            // take input from cleint socket
            in = new DataInputStream(new BufferedInputStream(socket.getInputStream()));

            String line = "";
            while (!line.equals("Over"))
            {
                try{
                    line = in.readUTF();
                    System.out.println("Closing connection");
                }
                catch(IOException i)
                {
                    System.out.println(i);
                }

            }
            System.out.println("Closing Connection:");
            // close connection
            socket.close();
            in.close();
        }
        catch(IOException i){
            System.out.println(i);
        }

    }
    public static void main(String [] args){
        Server2 server = new Server2(5000);
    }

}
