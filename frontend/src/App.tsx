import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './Layout';
import { Dashboard } from './pages/Dashboard';
import { Analysis } from './pages/Analysis';
export default function App(){return <BrowserRouter><Routes><Route path="/" element={<Layout/>}><Route index element={<Dashboard/>}/><Route path="analysis" element={<Analysis/>}/><Route path="*" element={<p>Page not found. Return to the evidence dashboard.</p>}/></Route></Routes></BrowserRouter>}
