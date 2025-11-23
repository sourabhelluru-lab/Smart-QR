package com.example.demo.models;

public class TabletInfo {
    private String name;
    private String dosage;
    private String timing;

    public TabletInfo() {}

    public TabletInfo(String name, String dosage, String timing) {
        this.name = name;
        this.dosage = dosage;
        this.timing = timing;
    }

    public String getName() { 
        return name; 
    }

    public void setName(String name) { 
        this.name = name; 
    }

    public String getDosage() { 
        return dosage; 
    }

    public void setDosage(String dosage) { 
        this.dosage = dosage; 
    }

    public String getTiming() { 
        return timing; 
    }

    public void setTiming(String timing) { 
        this.timing = timing; 
    }
}

