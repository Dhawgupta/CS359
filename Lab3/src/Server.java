import java.io.*;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.UnknownHostException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;



public class Server{

    private static int noThreads = 0;
    static List<String> IPA; // ip address to block
    static String defaultFile; // the default file to display from the browser
    private ServerSocket serverSocket;
    private int port;
    public static void main(String [] args) throws IOException {
        Server server = new Server(5000, "./ConfigurationFile.txt");
        server.startMultiThreadedServer();

    }

    private static void readConfigFile(String configFile){
        File conf = new File(configFile);
        String configurations = "";
        BufferedReader reader;
        try{
            reader = new BufferedReader(new FileReader(conf));
            String line = null;
            while (!(line = reader.readLine()).isEmpty()){
                configurations += line + "\n";
            }
            reader.close();



        }
        catch (Exception e){}
        System.out.println(configurations);
        noThreads =  Integer.parseInt(configurations.split("\n")[0].split("=")[1]);
        String str = configurations.split("\n")[1].split("=")[1];
        IPA = new ArrayList<String>(Arrays.asList(str.split("\\s*,\\s*")));
        defaultFile = configurations.split("\n")[2].split("=")[1];

        System.out.println(noThreads + "   \n" + IPA.toString()  + "    \n" + defaultFile + "   \n");

    }

    public Server(int port, String configFile){
        this.port = port;
        Server.readConfigFile(configFile);
    }

    public void startMultiThreadedServer() throws IOException{
        serverSocket = new ServerSocket(port);
        System.out.println("Starting MultiThreaded Server ...");
        while(true){
            try{
//                if (SocketHandler.counter <  noThreads) {
//                    System.out.println("Waiting for Client .....");
//                    System.out.println("========================");
//
//                    Socket client = serverSocket.accept();
//                    System.out.println("Creating a thread");
//                    Thread thread = new Thread(new SocketHandler(client));
//                    SocketHandler.counter += 1;
//                    thread.start();
//                }
//                else{
//                    System.out.println("Server Full wait");
//
//                }

                    System.out.println("Waiting for Client .....");
                    System.out.println("========================");

                    Socket client = serverSocket.accept();
                    if (SocketHandler.counter < noThreads) {
                        System.out.println("Creating a thread");
                        Thread thread = new Thread(new SocketHandler(client));
                        SocketHandler.counter += 1;
                        thread.start();
                    }
                    else{
                        BufferedWriter response = new BufferedWriter(new OutputStreamWriter(client.getOutputStream()));
                        StringBuilder sb = new StringBuilder();
                        constructResponseHeader(503,sb);
                        sb.append("The Server seems to full at the moment try later\r\n\r\n");
                        System.out.println(sb.toString());
                        response.write(sb.toString());
                        sb.setLength(0);
//                        response.write("The Server seems to full at the moment try later\r\n\r\n");
                        response.flush();
                        response.close();
                        client.close();
                    }


            }
            catch(Exception e){}
        }
    }

    public void serverStart() throws IOException {
        serverSocket = new ServerSocket(port);
        try{
            System.out.println("Waiting for Client .....");
            System.out.println("=======================");

            Socket client = serverSocket.accept();

            BufferedReader request = new BufferedReader(new InputStreamReader( client.getInputStream()));
            BufferedWriter response = new BufferedWriter(new OutputStreamWriter(client.getOutputStream()));

            String putDataFromClient = "";
            String requestHeader = "";
            String temp = ".";
            while(!temp.equals("")){
                temp = request.readLine();
//                System.out.println(temp);
                requestHeader += temp+"\n";

            }
            StringBuilder sb = new StringBuilder();
            if(requestHeader.split("\n")[0].contains("GET") && checkURL(requestHeader)){

                // get the correct page
                String file = requestHeader.split("\n")[0].split(" ")[1].split("/")[1];
                constructResponseHeader(200,sb);
                response.write(sb.toString());
                response.write(getData(file));
                sb.setLength(0);
                response.flush();

            }
            else{
                // 404 page not found
                constructResponseHeader(404,sb);
                response.write(sb.toString());
                sb.setLength(0);
                response.flush();

            }
            request.close();
            response.close();
            client.close();
            serverSocket.close();
            serverStart();
            return;


        }
        catch(Exception i){
            serverSocket.close();
            serverStart();

        }
    }


    private String getData(String file) {
        File myFile = new File(file);
        String responseToClient = "";
        BufferedReader reader;

        System.out.println("Printing the File Path : " + myFile.getAbsolutePath());
        try {
            reader = new BufferedReader(new FileReader(myFile));
            String line = null;
            while (!(line = reader.readLine()).contains("</html>")) {
                responseToClient += line;
            }
            responseToClient += line;
//            System.out.println(responseToClient);
            reader.close();

        } catch (Exception e) {
            System.out.println("There is a problem");

        }
        return responseToClient;
    }

    private static boolean checkURL(String requestHeader){
        //new File("path/to/file.txt").isFile();
        String url;
        url = requestHeader.split("\n")[0].split(" ")[1].split("/")[1];
        url = ("./" + url);
//        System.out.println(url);
        boolean exists = new File(url).isFile();
//        System.out.println(exists);
        return exists;
    }

    private static void constructResponseHeader(int respondeCode, StringBuilder sb){
        if(respondeCode == 200){
            sb.append("HTTP/1.1 200 OK\r\n");
            sb.append("Date:" + getTimeStamp() + "\r\n");
            try {
                sb.append("Server:" + InetAddress.getLocalHost().getHostAddress() + "\r\n");
            } catch (UnknownHostException e) {
                e.printStackTrace();
                System.out.println("Problem with resolving Hostname");
            }
            sb.append("Content-Type: text/html\r\n");
            sb.append("Connection: Closed\r\n\r\n");

        }
        else if(respondeCode == 404){
            sb.append("HTTP/1.1 404 Not Found\r\n");
            sb.append("Date:" + getTimeStamp() + "\r\n");
            try {
                sb.append("Server:" + InetAddress.getLocalHost().getHostAddress() + "\r\n");
            } catch (UnknownHostException e) {
                e.printStackTrace();
                System.out.println("Problem with resolving Hostname");
            }
            sb.append("\r\n");
        }
        else if(respondeCode == 503){
            sb.append("HTTP/1.1 503 Service Unavailable\r\n");
            sb.append("Date:" + getTimeStamp() + "\r\n");
            try {
                sb.append("Server:" + InetAddress.getLocalHost().getHostAddress() + "\r\n");

                sb.append("Content-Type: text/html\r\n");
                sb.append("Connection: Closed\r\n\r\n");
            } catch (UnknownHostException e) {
                e.printStackTrace();
                System.out.println("Problem with resolving Hostname");
            }


        }
//        System.out.println(sb);

    }

    private static String getTimeStamp() {
        Date date = new Date();
        SimpleDateFormat sdf = new SimpleDateFormat("MM/dd/yyyy h:mm:ss a");
        String formattedDate = sdf.format(date);
        return formattedDate;
    }

}