"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Users, FileText, Download } from "lucide-react";

const COLORS = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];

export default function AdminDashboard() {
  const [resumes, setResumes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    try {
      const response = await axios.get("http://localhost:8000/api/admin/resumes");
      setResumes(response.data);
    } catch (error) {
      console.error("Failed to fetch resumes", error);
    } finally {
      setLoading(false);
    }
  };

  const getRoleStats = () => {
    const roles: Record<string, number> = {};
    resumes.forEach((r) => {
      roles[r.predicted_role || "Unknown"] = (roles[r.predicted_role || "Unknown"] || 0) + 1;
    });
    return Object.keys(roles).map((key) => ({ name: key, value: roles[key] }));
  };

  const getExpStats = () => {
    const exps: Record<string, number> = {};
    resumes.forEach((r) => {
      exps[r.experience_level || "Unknown"] = (exps[r.experience_level || "Unknown"] || 0) + 1;
    });
    return Object.keys(exps).map((key) => ({ name: key, value: exps[key] }));
  };

  const downloadCSV = () => {
    const headers = ["ID,Name,Email,Mobile,Predicted Role,Score,Experience Level"];
    const rows = resumes.map(
      (r) =>
        `${r.id},${r.name},${r.email},${r.mobile_number},${r.predicted_role},${r.resume_score},${r.experience_level}`
    );
    const csvContent = "data:text/csv;charset=utf-8," + [headers, ...rows].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "resumes.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return <div className="min-h-screen bg-gray-900 flex items-center justify-center text-white">Loading Admin Dashboard...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
            <p className="text-gray-400">View and analyze applicant resumes</p>
          </div>
          <button
            onClick={downloadCSV}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg font-medium transition"
          >
            <Download className="w-5 h-5" />
            Export CSV
          </button>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 flex items-center gap-4">
            <div className="p-4 bg-blue-500/20 text-blue-400 rounded-xl">
              <Users className="w-8 h-8" />
            </div>
            <div>
              <p className="text-gray-400 text-sm">Total Resumes</p>
              <p className="text-3xl font-bold">{resumes.length}</p>
            </div>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 flex items-center gap-4">
            <div className="p-4 bg-emerald-500/20 text-emerald-400 rounded-xl">
              <FileText className="w-8 h-8" />
            </div>
            <div>
              <p className="text-gray-400 text-sm">Average Score</p>
              <p className="text-3xl font-bold">
                {resumes.length > 0 
                  ? (resumes.reduce((a, b) => a + (b.resume_score || 0), 0) / resumes.length).toFixed(1) 
                  : 0}
              </p>
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 h-96 flex flex-col">
            <h3 className="text-lg font-semibold mb-4">Predicted Roles Distribution</h3>
            <div className="flex-1">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={getRoleStats()} cx="50%" cy="50%" outerRadius={100} fill="#8884d8" dataKey="value" label>
                    {getRoleStats().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 h-96 flex flex-col">
            <h3 className="text-lg font-semibold mb-4">Experience Level Distribution</h3>
            <div className="flex-1">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={getExpStats()} cx="50%" cy="50%" outerRadius={100} fill="#8884d8" dataKey="value" label>
                    {getExpStats().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[(index + 2) % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Table Row */}
        <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
          <div className="p-6 border-b border-gray-700">
            <h3 className="text-lg font-semibold">Applicant Database</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-300">
              <thead className="bg-gray-900/50 text-gray-400">
                <tr>
                  <th className="px-6 py-4 font-medium">Name</th>
                  <th className="px-6 py-4 font-medium">Email</th>
                  <th className="px-6 py-4 font-medium">Mobile</th>
                  <th className="px-6 py-4 font-medium">Predicted Role</th>
                  <th className="px-6 py-4 font-medium">Exp Level</th>
                  <th className="px-6 py-4 font-medium text-right">Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {resumes.map((resume) => (
                  <tr key={resume.id} className="hover:bg-gray-700/50 transition">
                    <td className="px-6 py-4 font-medium text-white">{resume.name || "-"}</td>
                    <td className="px-6 py-4">{resume.email || "-"}</td>
                    <td className="px-6 py-4">{resume.mobile_number || "-"}</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 bg-gray-900 rounded-md border border-gray-600 text-xs">
                        {resume.predicted_role}
                      </span>
                    </td>
                    <td className="px-6 py-4">{resume.experience_level || "-"}</td>
                    <td className="px-6 py-4 text-right font-bold text-emerald-400">{resume.resume_score}</td>
                  </tr>
                ))}
                {resumes.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                      No resumes found in database.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}
