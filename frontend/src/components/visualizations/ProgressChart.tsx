import React from "react";
import { ProgressVisualization } from "@/contracts/api";
import { Card } from "../ui/Card";

interface ProgressChartProps {
  data: ProgressVisualization;
}

export function ProgressChart({ data }: ProgressChartProps) {
  const total = data.data.reduce((sum, item) => sum + item.value, 0);

  return (
    <Card className="p-4 w-full">
      <h3 className="text-sm font-medium text-foreground mb-4">{data.title}</h3>
      <div className="space-y-4">
        {data.data.map((item, idx) => {
          const percentage = total > 0 ? (item.value / total) * 100 : 0;
          return (
            <div key={idx} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="font-medium text-foreground">{item.label}</span>
                <span className="text-muted">{item.value.toLocaleString()}</span>
              </div>
              <div className="h-2 w-full bg-background rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary rounded-full transition-all duration-500" 
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
