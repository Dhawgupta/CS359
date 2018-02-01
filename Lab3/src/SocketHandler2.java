import javax.imageio.ImageIO;
import javax.imageio.stream.ImageInputStream;
import javax.imageio.stream.ImageOutputStream;
import java.awt.image.BufferedImage;
import java.io.*;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.text.SimpleDateFormat;
import java.util.Date;

public class SocketHandler2 implements Runnable {
    private Socket client;
    public SocketHandler2(Socket client){
        this.client = client;
    }

    public void run(){
        System.out.println("Threaded out for client : " +client.toString() + " with thread id as : " + Thread.currentThread().getName());
        try {
            processClient();
        } catch (IOException e) {
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
            if(requestHeader.split("\n")[0].contains("GET") && checkURL(requestHeader)){

                // get the correct page
                String file = requestHeader.split("\n")[0].split(" ")[1].split("/")[1];
                // file containst the file it can be either image or html type we will identify it
                boolean isImage = false;
                if(file.contains("jpg") || file.contains("jpeg"))
                    isImage = true;

                constructResponseHeader(200,sb,isImage);
                response.write(sb.toString());
                // getData will extract the data from file and append the data to the response
                if (!isImage) {
                    response.write(getData(file));
                    sb.setLength(0);
                    response.flush();
                }
//                response.flush();
                else{
                    File f1 = new File(file);
                    System.out.println("THe Path : " + f1.getAbsolutePath());
                    ImageInputStream imgStream = ImageIO.createImageInputStream(f1);
                    long size = imgStream.length();
                    BufferedImage bufferedImage = ImageIO.read(f1);
                    boolean success = ImageIO.write(bufferedImage, "gif",client.getOutputStream());

                }

            }
            else{
                // 404 page not found
                constructResponseHeader(404,sb,false);
                response.write(sb.toString());
                sb.setLength(0);
                response.flush();

            }

        }
        catch(Exception e){}
        client.close();


    }
    private static boolean checkURL(String header){
        String url;
        url = header.split("\n")[0].split(" ")[1].split("/")[1];
        url = ("./" + url);
        System.out.println(url);
        boolean exists = new File(url).isFile();
//        System.out.println(exists);
        return exists;
    }
    private static String getData(String file) {
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



    private void constructResponseHeader(int respondeCode, StringBuilder sb,boolean isImage) {
        if(respondeCode == 200){
//            if(!isImage) {
                sb.append("HTTP/1.1 200 OK\r\n");
                sb.append("Date:" + getTimeStamp() + "\r\n");
                try {
                    sb.append("Server:" + InetAddress.getLocalHost().getHostAddress() + "\r\n");
                } catch (UnknownHostException e) {
                    e.printStackTrace();
                    System.out.println("Problem with resolving Hostname");
                }
                sb.append("Content-Type: text/html\r\n");
                sb.append("Content-Type: image/jpeg\r\n");
                sb.append("Content-Type: image/jpg\r\n");
                sb.append("Content-Type: image/gif\r\n");

                sb.append("Connection: Closed\r\n\r\n");
//            }
//            else{
//                sb.append("HTTP/1.1 200 OK\r\n");
//                sb.append("Date:" + getTimeStamp() + "\r\n");
//                try {
//                    sb.append("Server:" + InetAddress.getLocalHost().getHostAddress() + "\r\n");
//                } catch (UnknownHostException e) {
//                    e.printStackTrace();
//                    System.out.println("Problem with resolving Hostname");
//                }
//                sb.append("Content-Type: image/jpeg\r\n");
//                sb.append("Content-Type: image/jpg\r\n");
//                sb.append("Content-Type: image/gif\r\n");
//                sb.append("Connection: Closed\r\n\r\n");
//
//            }
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
        System.out.println(sb);
    }

    private static String getTimeStamp(){
        Date date = new Date();
        SimpleDateFormat sdf = new SimpleDateFormat("MM/dd/yyyy h:mm:ss a");
        String formattedDate = sdf.format(date);
        return formattedDate;

    }



}
