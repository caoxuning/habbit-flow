package com.habitflow.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class MonthlyReportItem {
    private String month;
    private long count;
}
