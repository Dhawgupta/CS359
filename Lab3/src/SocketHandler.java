import java.io.*;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.concurrent.TimeUnit;

public class SocketHandler implements Runnable {
    public static int counter = 0;
    private Socket client;
    public SocketHandler(Socket client){
        this.client = client;
    }

    public void run(){
        System.out.println("Threaded out for client : " +client.toString() + " with thread id as : " + Thread.currentThread().getName());
        try {
            TimeUnit.SECONDS.sleep(5);
            processClient();

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }

    }
    private void processClient() throws IOException {

        try {
            BufferedReader request = new BufferedReader(new InputStreamReader(client.getInputStream()));
            BufferedWriter response = new BufferedWriter(new OutputStreamWriter(client.getOutputStream()));

            String putDataFromClient = "";
            String requestHeader = "";
            String temp = ".";
            while (!temp.equals("")) {
                temp = request.readLine();
//                System.out.println(temp);
                requestHeader += temp + "\n";
            }
            System.out.print("The Header from Threadid : " + Thread.currentThread().getName()  + "is" +
                    "\n" + requestHeader);

            // now we will process th header
            // string builder will conatin our response
            StringBuilder sb = new StringBuilder();
            // first condition checks wether is it a valid GET request or not
            //checkURL checks the file path

            if (checkClientValidity()) { // if client is not blocked grant access


                if (requestHeader.split("\n")[0].contains("GET") && checkURL(requestHeader)) {

                    // get the correct page
                    String file = requestHeader.split("\n")[0].split(" ")[1];
                    constructResponseHeader(200, sb);
                    response.write(sb.toString());
                    // getData will extract the data from file and append the data to the response

                    response.write(getData(file));
                    sb.setLength(0);
                    response.flush();

                } else {
                    // 404 page not found
                    constructResponseHeader(404, sb);
                    response.write(sb.toString());
                    sb.setLength(0);
                    response.flush();
                    response.close();
                    client.close();


                }
            }
            else{ // if the IP address is blocked send a request for denial of service
                constructResponseHeader(403, sb);
                response.write(sb.toString());
                sb.setLength(0);
                response.flush();
                response.close();
                client.close();
            }

        }
        catch(Exception e){}
        client.close();
        counter -= 1; // dicrementing the counter


    }
    private boolean checkClientValidity(){
//        Server.IPA contains the IP address to be blocked
        String addressOfClient = client.getInetAddress().getHostAddress();
        System.out.println("THIS IS ADDRESS : " + client.getInetAddress().getHostAddress() +" " +  (!Server.IPA.contains(addressOfClient)));

        return !Server.IPA.contains(addressOfClient);

//        return true;

    }
    private static boolean checkURL(String header){
        String url;
        url = header.split("\n")[0].split(" ")[1];
        if (url.equals("/")){
            url = Server.defaultFile;
            return true;
        }

        url = header.split("\n")[0].split(" ")[1].split("/")[1];
        url = ("./" + url);
        System.out.println(url);
        boolean exists = new File(url).isFile();
//        System.out.println(exists);
        return exists;
    }
    private static String getData(String file) {
        if (file.equals("/")){
            file = Server.defaultFile;
        }
        else
            file = "." + file;
        System.out.println(file);
        File myFil = new File(file);
        // extarct the html file to reponse to client
        String responseToClient = "";
        BufferedReader reader;

        System.out.println("Printing the File Path : " + myFil.getAbsolutePath());
        try {
            reader = new BufferedReader(new FileReader(myFil));
            String line = null;
            while (!(line = reader.readLine()).contains("</html>")) {
                responseToClient += line;
            }
            responseToClient += line;
//            System.out.println(responseToClient);
            reader.close();

        } catch (Exception e) {
            System.out.println("There is a problem while reading the file");

        }
        return responseToClient;
    }



    private void constructResponseHeader(int respondeCode, StringBuilder sb) {
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
        else if(respondeCode == 403){
            sb.append("HTTP/1.1 403 Forbidden\r\n");
            sb.append("Date:" + getTimeStamp() + "\r\n");
            try {
                sb.append("Server:" + InetAddress.getLocalHost().getHostAddress() + "\r\n");
            } catch (UnknownHostException e) {
                e.printStackTrace();
                System.out.println("Problem with resolving Hostname");
            }
            sb.append("\r\n");


        }
        System.out.println(sb);
    }

    private static String getTimeStamp(){
        Date date = new Date();
        SimpleDateFormat sdf = new SimpleDateFormat("MM/dd/yyyy h:mm:ss a");
        String formattedDate = sdf.format(date);
        return formattedDate;

    }



}
