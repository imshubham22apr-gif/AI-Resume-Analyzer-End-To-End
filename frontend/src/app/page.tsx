"use client";

import { useState, useRef } from "react";
import Velaris from "@/components/ui/Velaris";
import { UploadCloud, FileText, CheckCircle, Loader2, ArrowDown, ArrowUpRight } from "lucide-react";
import axios from "axios";
import { motion } from "framer-motion";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === "application/pdf") {
        setFile(droppedFile);
      } else {
        alert("Please upload a PDF file.");
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("resume", file);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await axios.post(`${apiUrl}/api/analyze`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setResult(response.data);
      // Auto-scroll to results logic could go here, but React state shift is instant enough for now.
    } catch (error) {
      console.error("Error analyzing resume", error);
      alert("Failed to analyze resume. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const chapterVariants = {
    hidden: { opacity: 0, y: 30, filter: "blur(5px)" },
    visible: { opacity: 1, y: 0, filter: "blur(0px)", transition: { duration: 0.8, ease: "easeOut" as const } }
  };

  return (
    <main className="relative min-h-screen bg-black text-white selection:bg-emerald-500/30 font-[family-name:var(--font-geist-sans)]">
      {/* Fixed Background */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <Velaris colors={["#10b981", "#059669", "#047857", "#000000"]} speed={1.5} grain={0.25} />
        {/* Subtle Vignette Overlay */}
        <div className="absolute inset-0 bg-radial-gradient from-transparent to-black opacity-80" />
      </div>

      {/* Scrollable Content */}
      <div className="relative z-10 w-full">
        
        {!result ? (
          <>
            {/* Chapter 00: Hero */}
            <section className="min-h-screen flex flex-col justify-center px-6 md:px-20 max-w-5xl mx-auto py-32">
              <motion.article 
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, amount: 0.3 }}
                variants={chapterVariants}
                className="space-y-6"
              >
                <h1 className="text-5xl md:text-7xl font-medium tracking-tight leading-tight">
                  Unlock your true <br/> professional trajectory.
                </h1>
                <p className="text-lg md:text-xl text-white/60 max-w-3xl leading-relaxed">
                  Hi, my name is Aashish. Welcome to AI Resume Analyzer! I have built this to help my friends and fellow juniors make their resumes align with their goals and target job roles. I process your unstructured resume data into structured insights. Using advanced NLP, I predict your ideal role, score your profile, and map the skills you need to bridge the gap.
                </p>
                <div className="pt-8">
                  <button 
                    onClick={() => {
                      document.getElementById("upload-section")?.scrollIntoView({ behavior: "smooth" });
                    }}
                    className="flex items-center gap-3 font-[family-name:var(--font-geist-mono)] text-sm uppercase tracking-widest hover:text-emerald-400 transition-colors"
                  >
                    Enter the field <ArrowDown className="w-4 h-4" />
                  </button>
                </div>
              </motion.article>
            </section>

            {/* Chapter 01: Upload */}
            <section id="upload-section" className="min-h-screen flex flex-col justify-center px-6 md:px-20 max-w-5xl mx-auto py-32">
              <motion.article 
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, amount: 0.3 }}
                variants={chapterVariants}
                className="space-y-12"
              >
                <h2 className="text-4xl md:text-5xl font-medium tracking-tight">Provide the raw material.</h2>
                
                <div 
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                  onClick={() => document.getElementById("file-upload")?.click()}
                  className="w-full h-80 border border-white/10 bg-white/[0.02] backdrop-blur-md flex flex-col items-center justify-center cursor-pointer hover:bg-white/[0.05] hover:border-emerald-500/50 transition-all duration-500 group"
                >
                  {file ? (
                    <div className="flex flex-col items-center space-y-4">
                      <CheckCircle className="w-12 h-12 text-emerald-400" />
                      <p className="font-[family-name:var(--font-geist-mono)] text-lg">{file.name}</p>
                      <p className="text-sm text-white/40">{(file.size / 1024 / 1024).toFixed(2)} MB ALLOCATED</p>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center space-y-6 text-white/50 group-hover:text-white/80 transition-colors">
                      <UploadCloud className="w-12 h-12" />
                      <div className="text-center font-[family-name:var(--font-geist-mono)]">
                        <p className="text-sm uppercase tracking-widest">Select or drop PDF file</p>
                        <p className="text-xs mt-2 opacity-50">INITIALIZING SECURE TRANSFER</p>
                      </div>
                    </div>
                  )}
                  <input
                    id="file-upload"
                    type="file"
                    accept="application/pdf"
                    className="hidden"
                    onChange={handleFileChange}
                  />
                </div>

                <div className="flex justify-end">
                  <button
                    onClick={handleSubmit}
                    disabled={!file || loading}
                    className="flex items-center gap-3 font-[family-name:var(--font-geist-mono)] text-sm uppercase tracking-widest disabled:opacity-30 disabled:cursor-not-allowed hover:text-emerald-400 transition-colors"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        Commence Analysis <ArrowUpRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </div>
              </motion.article>
            </section>
          </>
        ) : (
          /* Results Chapter */
          <section className="min-h-screen pt-32 pb-20 px-6 md:px-20 max-w-6xl mx-auto">
            <motion.article 
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={chapterVariants}
              className="space-y-12"
            >
              <div className="flex flex-col md:flex-row md:items-end justify-between gap-8 border-b border-white/10 pb-8">
                <div>
                  <div className="flex flex-col font-[family-name:var(--font-geist-mono)] text-xs tracking-widest text-emerald-400 mb-6">
                    <span>//02</span>
                    <span>ANALYSIS COMPLETE / DATA EXTRACTED</span>
                  </div>
                  <h2 className="text-4xl md:text-6xl font-medium tracking-tight">System output.</h2>
                </div>
                <button 
                  onClick={() => {setResult(null); setFile(null);}}
                  className="font-[family-name:var(--font-geist-mono)] text-xs uppercase tracking-widest text-white/50 hover:text-white transition-colors"
                >
                  [ RESTART PROCESS ]
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                
                {/* Score & Profile - Left Col */}
                <div className="lg:col-span-4 space-y-8">
                  <div className="border border-white/10 bg-white/[0.02] backdrop-blur-md p-8 flex flex-col gap-8">
                    <div>
                      <span className="font-[family-name:var(--font-geist-mono)] text-xs text-white/50 uppercase tracking-widest">Candidate Matrix</span>
                      <div className="mt-4 space-y-2 text-lg">
                        <p>{result.name || "UNIDENTIFIED"}</p>
                        <p className="text-white/70 text-sm break-all">{result.email || "NO SIGNAL"}</p>
                        <p className="text-white/70 text-sm">{result.mobile_number || "NO SIGNAL"}</p>
                      </div>
                    </div>
                    
                    <div className="border-t border-white/10 pt-8">
                      <span className="font-[family-name:var(--font-geist-mono)] text-xs text-white/50 uppercase tracking-widest">Match Score</span>
                      <div className="mt-4 flex items-baseline gap-2">
                        <span className="text-6xl font-medium text-emerald-400">{result.resume_score || 0}</span>
                        <span className="text-white/40 font-[family-name:var(--font-geist-mono)]">/100</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Insights - Right Col */}
                <div className="lg:col-span-8 space-y-8">
                  <div className="border border-white/10 bg-white/[0.02] backdrop-blur-md p-8 flex flex-col gap-8">
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      <div>
                        <span className="font-[family-name:var(--font-geist-mono)] text-xs text-white/50 uppercase tracking-widest">Predicted Role</span>
                        <p className="mt-4 text-2xl md:text-3xl font-medium text-emerald-400">{result.predicted_role || "Unknown"}</p>
                      </div>
                      <div>
                        <span className="font-[family-name:var(--font-geist-mono)] text-xs text-white/50 uppercase tracking-widest">Experience Level</span>
                        <p className="mt-4 text-2xl md:text-3xl font-medium">{result.experience_level || "Unknown"}</p>
                      </div>
                    </div>

                    <div className="border-t border-white/10 pt-8">
                      <span className="font-[family-name:var(--font-geist-mono)] text-xs text-white/50 uppercase tracking-widest">Identified Nodes (Skills)</span>
                      <div className="mt-6 flex flex-wrap gap-2">
                        {result.skills && result.skills.length > 0 ? (
                          result.skills.map((skill: string, idx: number) => (
                            <span key={idx} className="font-[family-name:var(--font-geist-mono)] text-xs px-3 py-1.5 border border-white/20 text-white/80 uppercase">
                              {skill}
                            </span>
                          ))
                        ) : (
                          <span className="text-white/50 text-sm">NO NODES DETECTED</span>
                        )}
                      </div>
                    </div>

                    <div className="border-t border-emerald-500/20 pt-8">
                      <span className="font-[family-name:var(--font-geist-mono)] text-xs text-emerald-400/80 uppercase tracking-widest">Optimization Pathway (Missing Skills)</span>
                      <div className="mt-6 flex flex-wrap gap-2">
                        {result.recommended_skills && result.recommended_skills.length > 0 ? (
                          result.recommended_skills.map((skill: string, idx: number) => (
                            <span key={idx} className="font-[family-name:var(--font-geist-mono)] text-xs px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 uppercase">
                              + {skill}
                            </span>
                          ))
                        ) : (
                          <span className="text-white/50 text-sm">SYSTEM OPTIMIZED. NO NEW PATHWAYS REQUIRED.</span>
                        )}
                      </div>
                    </div>
                    
                    {/* NEW: Actionable Enhancements from Backend */}
                    {(result.strengths?.length > 0 || result.improvements?.length > 0) && (
                      <div className="border-t border-white/10 pt-8 grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div>
                          <span className="font-[family-name:var(--font-geist-mono)] text-xs text-emerald-400 uppercase tracking-widest">Core Strengths</span>
                          <ul className="mt-4 space-y-3">
                            {result.strengths?.map((item: string, idx: number) => (
                              <li key={idx} className="text-sm text-white/80 flex items-start gap-2">
                                <span className="text-emerald-400 mt-0.5">▹</span> {item}
                              </li>
                            ))}
                            {!result.strengths?.length && <li className="text-sm text-white/40">NO SIGNIFICANT STRENGTHS DETECTED</li>}
                          </ul>
                        </div>
                        <div>
                          <span className="font-[family-name:var(--font-geist-mono)] text-xs text-amber-400 uppercase tracking-widest">Areas for Improvement</span>
                          <ul className="mt-4 space-y-3">
                            {result.improvements?.map((item: string, idx: number) => (
                              <li key={idx} className="text-sm text-white/80 flex items-start gap-2">
                                <span className="text-amber-400 mt-0.5">▹</span> {item}
                              </li>
                            ))}
                            {!result.improvements?.length && <li className="text-sm text-white/40">NO SIGNIFICANT DEFICIENCIES DETECTED</li>}
                          </ul>
                        </div>
                      </div>
                    )}

                  </div>
                </div>

              </div>
            </motion.article>
          </section>
        )}
      </div>
    </main>
  );
}

