// This file was created to manage all of the the task i want to complete for the project. 

import java.util.ArrayList; // For managing the list of tasks
import java.util.List; // For using List interface
import java.io.File; // For file handling
import javax.xml.parsers.*; // For XML parsing
import org.w3c.dom.*; // For working with XML documents

public class TodoList { // Class to manage a todo list
// INSTANCE VARIABLES //
    private ArrayList<String> todo = new ArrayList<>();// List to store todo items
    private static DocumentBuilderFactory factory; // Factory for creating document builders
    
    static {
        factory = DocumentBuilderFactory.newInstance(); // Initialize the factory
        factory.setNamespaceAware(true); // Set the factory to be namespace aware
        factory.setValidating(false); // Disable validation
    }

    public void addTask(String item) { // Method to add a task
        if (item != null && !item.trim().isEmpty()) { // Check for valid input by trimming the whitespace within the string
            todo.add(item.trim());// Add a trimmed item to the list
        }
    }

    public void addTasks(String... items) {
        for(String item : items) {
            if(item != null && !item.trim().isEmpty()) {
                todo.add(item.trim());
            }
        }
    }
    
    public void deleteTask(int index) { // Method to delete a task by index
        if (index >= 0 && index < todo.size()) { // Check for valid index
            todo.remove(index); // Remove the item at the specified index
        }
    }
    
    public String[] getTasks() { // Method to get all tasks as an array
        return todo.toArray(new String[todo.size()]); // Convert the list to an array and return it
    }
    
    public ArrayList<String> getTasksList() {
        return new ArrayList<>(todo);
    }

    public int size() { // Method to get the number of tasks
        return todo.size(); // Return the size of the todo list
    }
    
    public void importFromSVG(String filePath) { // Method to import tasks from an SVG file
        try { // Try-catch block for handling exceptions
            File svgFile = new File(filePath); // Create a File object for the SVG file
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance(); // Create a DocumentBuilderFactory instance
            DocumentBuilder builder = factory.newDocumentBuilder(); // Create a Document Builder instance
            Document doc = builder.parse(svgFile); // Parse the SVG file into a Document object.
            
            NodeList textNodes = doc.getElementsByTagName("text"); // Get all <text> elements from the SVG
            int length = textNodes.getLength();
            
            todo.ensureCapacity(todo.size() + length);

            for(int i=0; i<length; i++) {
                Element textElement = (Element) textNodes.item(i);
                String content = textElement.getTextContent();
                if(content != null && !content.trim().isEmpty()) {
                    todo.add(content.trim());
                }
            }
        } catch (Exception e) { // Catch any exceptions that occur during file handling or parsing
            e.printStackTrace(); // Print the stack trace for debugging
        }
    }
/*
    public void completeTask(int index) {
        if(index>=0 && index <todo.size()) {
            String task = todo.get(index);
            if(!task.startsWith())
        }
    }*/

    public void showWithCheckboxes() {
    if(todo.isEmpty()) {
        System.out.println("Yayyyy no more tasks to do. We have finished! insert: celebration");
        return;
    }
    int width = 41;
    System.out.println("╔═══════════════════════════════════════╗");
    System.out.println("║              TODO LIST                ║");
    System.out.println("╠═══════════════════════════════════════╣");
    for(int i=0; i<todo.size();i++) {
        String fullTask = "☐ " + (i+1) + ". " + todo.get(i);
        int maxContentWidth = width - 4; // Account for "║ " and " ║"
        
        if(fullTask.length() <= maxContentWidth) {
            // Task fits on one line
            int padding = maxContentWidth - fullTask.length();
            System.out.println("║ " + fullTask + " ".repeat(padding) + " ║");
        } else {
            // Task needs to wrap - split into multiple lines
            String prefix = "☐ " + (i+1) + ". ";
            String content = todo.get(i);
            int contentWidth = maxContentWidth - prefix.length();
            
            // First line with prefix
            System.out.println("║ " + prefix + content.substring(0, Math.min(contentWidth, content.length())) + " ║");
            
            // Remaining lines indented
            int remaining = content.length() - contentWidth;
            int startIndex = contentWidth;
            String indent = "    "; // 4 spaces for indentation
            
            while(remaining > 0) {
                int endIndex = Math.min(startIndex + maxContentWidth - indent.length(), content.length());
                String line = indent + content.substring(startIndex, endIndex);
                int padding = maxContentWidth - line.length();
                System.out.println("║ " + line + " ".repeat(padding) + " ║");
                remaining = content.length() - endIndex;
                startIndex = endIndex;
            }
        }
    }
    System.out.println("╚═══════════════════════════════════════╝");
}
<<<<<<< HEAD
}
=======
}
>>>>>>> b4a07e3 (BANG)
