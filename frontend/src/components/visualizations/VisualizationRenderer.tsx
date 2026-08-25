import React from "react";
import { VisualizationData } from "@/contracts/api";
import { KpiCard } from "./KpiCard";
import { BarChart } from "./BarChart";
import { LineChart } from "./LineChart";
import { ProgressChart } from "./ProgressChart";
import { DataTable } from "./DataTable";

interface VisualizationRendererProps {
  data: VisualizationData[];
}

export function VisualizationRenderer({ data }: VisualizationRendererProps) {
  if (!data || data.length === 0) return null;

  const kpis = data.filter((d) => d.type === "kpi");
  const others = data.filter((d) => d.type !== "kpi");

  return (
    <div className="flex flex-col gap-6 mt-6 mb-4 w-full">
      {kpis.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {kpis.map((kpi, idx) => (
            <KpiCard key={idx} data={kpi as any} />
          ))}
        </div>
      )}

      {others.map((viz, idx) => {
        switch (viz.type) {
          case "bar":
            return <BarChart key={idx} data={viz as any} />;
          case "line":
            return <LineChart key={idx} data={viz as any} />;
          case "progress":
            return <ProgressChart key={idx} data={viz as any} />;
          case "table":
            return <DataTable key={idx} data={viz as any} />;
          default:
            return null;
        }
      })}
    </div>
  );
}
