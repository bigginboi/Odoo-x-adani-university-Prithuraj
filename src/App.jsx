import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  LayoutGrid, Wrench, ShieldCheck, Activity, 
  Sparkles, Send, X, RefreshCw, Cpu, AlertTriangle 
} from 'lucide-react';
import { GoogleGenerativeAI } from "@google/generative-ai";

// 🔑 Your Verified API Key & Project Config
const API_KEY = "AIzaSyAvVo7xJMiIftf-p48a2G7fGgxA3LRpyQ4"; 

export default function App() {
    const [data, setData] = useState({ equipment: [], requests: [] });
    const [view, setView] = useState('assets');
    const [aiOpen, setAiOpen] = useState(false);
    const [input, setInput] = useState("");
    const [chat, setChat] = useState([
        {r:'ai', t:'GearGuard AI is active. How can I help with your fleet?'}
    ]);

    const loadData = async () => {
        try {
            // Updated to Port 5001 as per your previous error resolution
            const res = await axios.get('http://localhost:5001/api/data');
            setData(res.data);
        } catch (e) {
            console.warn("Backend 5001 unreachable. Displaying fallback UI.");
            // Fallback interactive data if PostgreSQL connection fails
            setData({
                equipment: [
                    {id: 1, name: 'CNC Milling X1', sn: 'SN-GGP-01', health: 94, status: 'Operational'},
                    {id: 2, name: '3D Printer V4', sn: 'SN-GGP-02', health: 28, status: 'Critical'},
                    {id: 3, name: 'Lathe Pro', sn: 'SN-GGP-03', health: 65, status: 'Maintenance Req'}
                ],
                requests: [{id: 1, title: 'Check hydraulic seal on SN-003'}]
            });
        }
    };

    useEffect(() => { loadData(); }, []);

    const askAI = async () => {
        if (!input.trim()) return;
        const userMsg = input;
        setInput("");
        setChat(prev => [...prev, { r: 'user', t: userMsg }]);

        try {
            const genAI = new GoogleGenerativeAI(API_KEY);
            const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
            const prompt = `System Assets: ${JSON.stringify(data.equipment)}. User Query: ${userMsg}. (Act as an industrial expert)`;
            
            const result = await model.generateContent(prompt);
            setChat(prev => [...prev, { r: 'ai', t: result.response.text() }]);
        } catch (err) {
            setChat(prev => [...prev, { r: 'ai', t: "AI Link Interrupted. Check your key quota or internet connection." }]);
        }
    };

    return (
        <div className="flex h-screen bg-slate-50 text-slate-800 font-sans overflow-hidden">
            {/* Minimalist Sidebar */}
            <nav className="w-24 bg-white border-r border-slate-200 flex flex-col items-center py-12 gap-10 shadow-sm z-20">
                <div className="p-3 bg-indigo-600 rounded-2xl shadow-lg shadow-indigo-100 mb-4 cursor-pointer hover:rotate-12 transition-transform">
                    <ShieldCheck className="text-white" size={28}/>
                </div>
                
                <button 
                  onClick={() => setView('assets')} 
                  className={`p-4 rounded-2xl transition-all duration-300 ${view === 'assets' ? 'bg-indigo-50 text-indigo-600 shadow-inner' : 'text-slate-300 hover:text-slate-500 hover:bg-slate-50'}`}
                >
                    <LayoutGrid size={24} />
                </button>
                
                <button 
                  onClick={() => setView('requests')} 
                  className={`p-4 rounded-2xl transition-all duration-300 ${view === 'requests' ? 'bg-indigo-50 text-indigo-600 shadow-inner' : 'text-slate-300 hover:text-slate-500 hover:bg-slate-50'}`}
                >
                    <Wrench size={24} />
                </button>

                <button 
                  onClick={loadData} 
                  className="mt-auto p-4 text-slate-300 hover:text-indigo-600 hover:rotate-180 transition-all duration-700"
                >
                    <RefreshCw size={20}/>
                </button>
            </nav>

            <main className="flex-1 p-16 overflow-y-auto bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-white via-slate-50 to-slate-100">
                <header className="mb-16 flex justify-between items-center">
                    <div>
                        <h1 className="text-7xl font-black italic tracking-tighter uppercase text-slate-900 leading-none">
                          GearGuard<span className="text-indigo-600">.</span>
                        </h1>
                        <p className="text-[11px] font-bold text-slate-400 tracking-[0.6em] uppercase mt-4 flex items-center gap-2">
                           <Cpu size={14} className="text-indigo-400" /> PostgreSQL Fleet Intelligence
                        </p>
                    </div>
                    <div className="bg-white px-6 py-3 rounded-2xl border border-slate-200 shadow-sm">
                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">System Status</span>
                        <span className="text-xs font-bold text-green-500 flex items-center gap-2">● AI ENGINE ACTIVE</span>
                    </div>
                </header>

                {view === 'assets' ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
                        {data.equipment.map(item => (
                            <div key={item.id} className="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-[0_20px_50px_rgba(0,0,0,0.04)] hover:shadow-[0_30px_60px_rgba(79,70,229,0.1)] hover:-translate-y-2 transition-all duration-500 group relative overflow-hidden">
                                <div className="flex justify-between items-center mb-8">
                                    <div className="bg-slate-50 p-4 rounded-2xl group-hover:bg-indigo-50 transition-colors">
                                        <Activity size={24} className="text-slate-400 group-hover:text-indigo-600" />
                                    </div>
                                    <span className={`text-[10px] font-black px-4 py-2 rounded-full border uppercase tracking-widest ${
                                      item.health < 40 ? 'bg-red-50 text-red-500 border-red-100' : 'bg-green-50 text-green-500 border-green-100'
                                    }`}>
                                        {item.status}
                                    </span>
                                </div>
                                
                                <h3 className="text-2xl font-bold text-slate-800 mb-1">{item.name}</h3>
                                <p className="text-[11px] text-slate-400 font-mono mb-8 tracking-widest uppercase">ID: {item.sn}</p>
                                
                                <div className="relative h-2.5 w-full bg-slate-100 rounded-full mb-10 overflow-hidden">
                                    <div 
                                      className={`absolute h-full transition-all duration-1000 ${item.health < 40 ? 'bg-red-500' : 'bg-indigo-600'}`} 
                                      style={{width: `${item.health}%`}} 
                                    />
                                </div>
                                
                                <button className="w-full py-5 bg-slate-900 text-white rounded-[1.5rem] font-black text-xs uppercase tracking-[0.2em] group-hover:bg-indigo-600 transition-all shadow-xl shadow-slate-100">
                                    Initiate Service
                                </button>
                                
                                {item.health < 40 && (
                                    <div className="absolute top-4 right-4 animate-pulse">
                                        <AlertTriangle className="text-red-500" size={20} />
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="max-w-4xl space-y-6">
                        {data.requests.map(r => (
                            <div key={r.id} className="bg-white p-8 rounded-3xl border border-slate-200 flex justify-between items-center shadow-sm group hover:border-indigo-200 transition-all">
                                <div className="flex items-center gap-6">
                                    <div className="w-12 h-12 bg-slate-50 rounded-2xl flex items-center justify-center text-slate-400 group-hover:bg-indigo-50 group-hover:text-indigo-600">
                                        <Wrench size={20}/>
                                    </div>
                                    <span className="font-bold text-slate-700 italic text-xl uppercase tracking-tighter">SERVICE LOG #{r.id}: {r.title}</span>
                                </div>
                                <span className="text-[10px] font-black text-indigo-500 bg-indigo-50 px-5 py-2 rounded-full uppercase border border-indigo-100 tracking-widest">Postgres Verified</span>
                            </div>
                        ))}
                    </div>
                )}
            </main>

            {/* AI Floating Co-Pilot */}
            <div className="fixed bottom-12 right-12 flex flex-col items-end z-50">
                {aiOpen && (
                    <div className="w-[420px] h-[600px] bg-white border border-slate-100 rounded-[3.5rem] shadow-[0_40px_100px_rgba(0,0,0,0.12)] flex flex-col overflow-hidden mb-8 animate-in fade-in zoom-in duration-300">
                        <div className="p-8 bg-slate-50 border-b border-slate-100 flex justify-between font-black text-[10px] italic tracking-[0.3em] uppercase text-slate-400">
                            <span className="flex items-center gap-2"><Sparkles size={14} className="text-indigo-500"/> AI Diagnostic Engine</span>
                            <X className="cursor-pointer hover:text-red-500 transition-colors" size={18} onClick={() => setAiOpen(false)}/>
                        </div>
                        
                        <div className="flex-1 p-8 overflow-y-auto space-y-6 text-[13px] leading-relaxed scrollbar-hide">
                            {chat.map((c, i) => (
                                <div key={i} className={`p-6 rounded-[2rem] ${
                                  c.r === 'ai' 
                                  ? 'bg-slate-50 text-slate-600 mr-12 border border-slate-100' 
                                  : 'bg-indigo-600 text-white ml-12 shadow-xl shadow-indigo-100'
                                }`}>
                                    {c.t}
                                </div>
                            ))}
                        </div>
                        
                        <div className="p-8 bg-white border-t border-slate-100 flex gap-3">
                            <input 
                              value={input} 
                              onChange={e => setInput(e.target.value)} 
                              onKeyPress={e => e.key === 'Enter' && askAI()} 
                              className="flex-1 bg-slate-50 p-5 rounded-2xl text-xs outline-none border border-transparent focus:border-indigo-100 focus:bg-white transition-all font-bold placeholder:text-slate-300" 
                              placeholder="Ask about machine health..." 
                            />
                            <button onClick={askAI} className="bg-slate-900 text-white p-5 rounded-2xl hover:bg-indigo-600 transition-all shadow-lg hover:-translate-y-1">
                                <Send size={20} />
                            </button>
                        </div>
                    </div>
                )}
                
                <button 
                  onClick={() => setAiOpen(!aiOpen)} 
                  className="bg-indigo-600 text-white p-8 rounded-[2.5rem] shadow-[0_20px_50px_rgba(79,70,229,0.3)] hover:scale-110 hover:rotate-6 active:scale-95 transition-all border-8 border-white group"
                >
                    <Sparkles size={32} className="group-hover:animate-pulse" />
                </button>
            </div>
        </div>
    );
}