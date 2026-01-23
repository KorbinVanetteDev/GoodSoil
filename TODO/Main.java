import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.geom.RoundRectangle2D;
import java.util.ArrayList;

public class Main extends JFrame {
    private TodoList todoList;
    private DefaultListModel<String> listModel;
    private JList<String> taskJList;
    private JTextField taskInput;
    private JButton addButton;
    private JButton deleteButton;
    private JButton clearButton;
    private JLabel counterLabel;
    private JLabel titleLabel;

    public Main() {
        todoList = new TodoList();
        
        // Add initial tasks
        todoList.addTask("Hack Club Project todo");
        todoList.addTask("This will help me manage everything I have planned out");
        
        // Set up the frame
        setTitle("TODO List - Hack Club");
        setSize(600, 700);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setResizable(true);
        
        // Initialize components
        initComponents();
        
        // Load existing tasks
        refreshList();
    }
    
    private void initComponents() {
        // Main panel with gradient background
        JPanel mainPanel = new JPanel(new BorderLayout(15, 15)) {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                Graphics2D g2d = (Graphics2D) g;
                g2d.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
                GradientPaint gp = new GradientPaint(0, 0, new Color(245, 247, 250), 0, getHeight(), new Color(235, 240, 248));
                g2d.setPaint(gp);
                g2d.fillRect(0, 0, getWidth(), getHeight());
            }
        };
        mainPanel.setOpaque(false);
        mainPanel.setBorder(new EmptyBorder(20, 20, 20, 20));
        
        // Header Panel
        JPanel headerPanel = new JPanel(new FlowLayout(FlowLayout.CENTER));
        headerPanel.setOpaque(false);
        
        titleLabel = new JLabel("✓ TODO LIST");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 32));
        titleLabel.setForeground(new Color(40, 60, 120));
        headerPanel.add(titleLabel);
        
        mainPanel.add(headerPanel, BorderLayout.NORTH);
        
        // Center panel for the list
        listModel = new DefaultListModel<>();
        taskJList = new JList<>(listModel);
        taskJList.setFont(new Font("Segoe UI", Font.PLAIN, 15));
        taskJList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        taskJList.setCellRenderer(new TaskCellRenderer());
        taskJList.setFixedCellHeight(45);
        
        JScrollPane scrollPane = new JScrollPane(taskJList);
        scrollPane.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(new Color(180, 190, 210), 2),
            new EmptyBorder(5, 5, 5, 5)
        ));
        scrollPane.setBackground(Color.WHITE);
        scrollPane.getViewport().setBackground(Color.WHITE);
        mainPanel.add(scrollPane, BorderLayout.CENTER);
        
        // Bottom panel
        JPanel bottomPanel = new JPanel(new BorderLayout(10, 10));
        bottomPanel.setOpaque(false);
        
        // Input panel
        JPanel inputPanel = new JPanel(new BorderLayout(8, 8));
        inputPanel.setOpaque(false);
        
        JLabel inputLabel = new JLabel("New Task:");
        inputLabel.setFont(new Font("Segoe UI", Font.BOLD, 12));
        inputLabel.setForeground(new Color(60, 80, 120));
        inputPanel.add(inputLabel, BorderLayout.WEST);
        
        JPanel inputFieldPanel = new JPanel(new BorderLayout());
        inputFieldPanel.setOpaque(false);
        
        taskInput = new JTextField();
        taskInput.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        taskInput.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(new Color(180, 190, 210), 2),
            new EmptyBorder(8, 12, 8, 12)
        ));
        taskInput.setBackground(Color.WHITE);
        
        addButton = new JButton("+ Add Task");
        addButton.setFont(new Font("Segoe UI", Font.BOLD, 13));
        addButton.setBackground(new Color(52, 152, 219));
        addButton.setForeground(Color.WHITE);
        addButton.setFocusPainted(false);
        addButton.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));
        addButton.setCursor(new Cursor(Cursor.HAND_CURSOR));
        addButton.setFocusable(false);
        
        // Hover effect
        addButton.addMouseListener(new MouseAdapter() {
            public void mouseEntered(MouseEvent e) {
                addButton.setBackground(new Color(41, 128, 185));
            }
            public void mouseExited(MouseEvent e) {
                addButton.setBackground(new Color(52, 152, 219));
            }
        });
        
        inputFieldPanel.add(taskInput, BorderLayout.CENTER);
        inputFieldPanel.add(addButton, BorderLayout.EAST);
        
        inputPanel.add(inputFieldPanel, BorderLayout.CENTER);
        
        // Button panel
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 15, 10));
        buttonPanel.setOpaque(false);
        
        deleteButton = new JButton("🗑 Delete");
        deleteButton.setFont(new Font("Segoe UI", Font.BOLD, 13));
        deleteButton.setBackground(new Color(231, 76, 60));
        deleteButton.setForeground(Color.WHITE);
        deleteButton.setFocusPainted(false);
        deleteButton.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));
        deleteButton.setCursor(new Cursor(Cursor.HAND_CURSOR));
        deleteButton.setFocusable(false);
        
        deleteButton.addMouseListener(new MouseAdapter() {
            public void mouseEntered(MouseEvent e) {
                deleteButton.setBackground(new Color(192, 57, 43));
            }
            public void mouseExited(MouseEvent e) {
                deleteButton.setBackground(new Color(231, 76, 60));
            }
        });
        
        clearButton = new JButton("🔄 Clear All");
        clearButton.setFont(new Font("Segoe UI", Font.BOLD, 13));
        clearButton.setBackground(new Color(155, 89, 182));
        clearButton.setForeground(Color.WHITE);
        clearButton.setFocusPainted(false);
        clearButton.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));
        clearButton.setCursor(new Cursor(Cursor.HAND_CURSOR));
        clearButton.setFocusable(false);
        
        clearButton.addMouseListener(new MouseAdapter() {
            public void mouseEntered(MouseEvent e) {
                clearButton.setBackground(new Color(108, 52, 131));
            }
            public void mouseExited(MouseEvent e) {
                clearButton.setBackground(new Color(155, 89, 182));
            }
        });
        
        buttonPanel.add(deleteButton);
        buttonPanel.add(clearButton);
        
        // Counter label
        counterLabel = new JLabel("Tasks: 0");
        counterLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        counterLabel.setForeground(new Color(52, 152, 219));
        
        JPanel counterPanel = new JPanel(new FlowLayout(FlowLayout.CENTER));
        counterPanel.setOpaque(false);
        counterPanel.add(counterLabel);
        
        bottomPanel.add(inputPanel, BorderLayout.NORTH);
        bottomPanel.add(buttonPanel, BorderLayout.CENTER);
        bottomPanel.add(counterPanel, BorderLayout.SOUTH);
        
        mainPanel.add(bottomPanel, BorderLayout.SOUTH);
        
        // Add main panel to frame
        add(mainPanel);
        
        // Event listeners
        addButton.addActionListener(e -> addTask());
        deleteButton.addActionListener(e -> deleteTask());
        clearButton.addActionListener(e -> clearAllTasks());
        
        taskInput.addActionListener(e -> addTask());
        
        // Double-click to mark as complete (visual indicator)
        taskJList.addMouseListener(new MouseAdapter() {
            public void mouseClicked(MouseEvent e) {
                if (e.getClickCount() == 2) {
                    int index = taskJList.locationToIndex(e.getPoint());
                    if (index >= 0) {
                        String task = listModel.get(index);
                        if (task.startsWith("☐")) {
                            listModel.set(index, task.replace("☐", "☑"));
                        } else if (task.startsWith("☑")) {
                            listModel.set(index, task.replace("☑", "☐"));
                        }
                    }
                }
            }
        });
    }
    
    private void addTask() {
        String task = taskInput.getText().trim();
        if (!task.isEmpty()) {
            todoList.addTask(task);
            listModel.addElement("☐ " + task);
            taskInput.setText("");
            taskInput.requestFocus();
            updateCounter();
        } else {
            JOptionPane.showMessageDialog(this, 
                "Please enter a task!", 
                "Empty Task", 
                JOptionPane.WARNING_MESSAGE);
        }
    }
    
    private void deleteTask() {
        int selectedIndex = taskJList.getSelectedIndex();
        if (selectedIndex >= 0) {
            todoList.deleteTask(selectedIndex);
            listModel.remove(selectedIndex);
            updateCounter();
        } else {
            JOptionPane.showMessageDialog(this, 
                "Please select a task to delete!", 
                "No Selection", 
                JOptionPane.WARNING_MESSAGE);
        }
    }
    
    private void clearAllTasks() {
        if (todoList.size() == 0) {
            JOptionPane.showMessageDialog(this, "No tasks to clear!", "Empty List", JOptionPane.INFORMATION_MESSAGE);
            return;
        }
        int result = JOptionPane.showConfirmDialog(this, 
            "Are you sure you want to delete all tasks?", 
            "Clear All Tasks", 
            JOptionPane.YES_NO_OPTION);
        
        if (result == JOptionPane.YES_OPTION) {
            listModel.clear();
            todoList = new TodoList();
            updateCounter();
        }
    }
    
    private void refreshList() {
        listModel.clear();
        ArrayList<String> tasks = todoList.getTasksList();
        for (String task : tasks) {
            listModel.addElement("☐ " + task);
        }
        updateCounter();
    }
    
    private void updateCounter() {
        counterLabel.setText("Tasks: " + todoList.size());
    }
    
    // Custom cell renderer for tasks
    private class TaskCellRenderer extends DefaultListCellRenderer {
        @Override
        public Component getListCellRendererComponent(JList<?> list, Object value, 
                int index, boolean isSelected, boolean cellHasFocus) {
            JLabel label = (JLabel) super.getListCellRendererComponent(
                list, value, index, isSelected, cellHasFocus);
            
            label.setBorder(new CompoundBorder(
                new LineBorder(new Color(220, 225, 235), 1),
                new EmptyBorder(10, 12, 10, 12)
            ));
            
            if (isSelected) {
                label.setBackground(new Color(52, 152, 219));
                label.setForeground(Color.WHITE);
            } else {
                label.setBackground(Color.WHITE);
                label.setForeground(new Color(50, 50, 70));
            }
            
            String text = value.toString();
            if (text.startsWith("☑")) {
                label.setForeground(new Color(150, 150, 150));
                label.setFont(label.getFont().deriveFont(Font.ITALIC));
            }
            
            return label;
        }
    }
    
    public static void main(String[] args) {
        // Use system look and feel
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        // Create and show GUI on the Event Dispatch Thread
        SwingUtilities.invokeLater(() -> {
            Main app = new Main();
            app.setVisible(true);
        });
    }
<<<<<<< HEAD
}
=======
}
>>>>>>> b4a07e3 (BANG)
