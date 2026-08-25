import React from "react";
import { KpiVisualization } from "@/contracts/api";
import { Card } from "../ui/Card";
import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";

interface KpiCardProps {
  data: KpiVisualization;
}

export function KpiCard({ data }: KpiCardProps) {
  return (
    <Card className="p-4 flex flex-col justify-between h-full min-w-0 flex-1">
      <h3 className="text-sm font-medium text-muted mb-2 break-words whitespace-normal" style={{ overflowWrap: "anywhere" }}>{data.title}</h3>
      <div className="flex items-baseline gap-2 mb-1">
        <span className="text-2xl font-bold tracking-tight text-foreground whitespace-normal break-words" style={{ overflowWrap: "anywhere" }}>{data.value}</span>
      </div>
      
      {(data.change || data.description) && (
        <div className="flex items-center gap-2 text-sm mt-1">
          {data.change && (
            <div
              className={`flex items-center font-medium ${
                data.change_direction === "up"
                  ? "text-green"
                  : data.change_direction === "down"
                  ? "text-red"
                  : "text-muted"
              }`}
            >
              {data.change_direction === "up" && <ArrowUpRight className="w-3 h-3 mr-1" />}
              {data.change_direction === "down" && <ArrowDownRight className="w-3 h-3 mr-1" />}
              {data.change_direction === "neutral" && <Minus className="w-3 h-3 mr-1" />}
              {data.change}
            </div>
          )}
          {data.description && (
            <span className="text-muted truncate">{data.description}</span>
          )}
        </div>
      )}
    </Card>
  );
}
