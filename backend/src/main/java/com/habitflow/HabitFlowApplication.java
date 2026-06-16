package com.habitflow;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.habitflow.mapper")
public class HabitFlowApplication {
    public static void main(String[] args) {
        SpringApplication.run(HabitFlowApplication.class, args);
    }
}
