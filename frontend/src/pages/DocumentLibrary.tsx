import React, { useState, useRef } from 'react';
import { 
  FolderGit2, 
  UploadCloud, 
  FileText, 
  Trash2, 
  Search, 
  Layers, 
  Eye, 
  X, 
  CheckCircle2, 
  AlertCircle,
  RotateCw,
  FileCode,
  File as FileIcon,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import { DocumentItem, DocumentChunk } from '../types';

interface DocumentLibraryProps {
  documents: DocumentItem[];
  onRefresh: () => void;
}

export const DocumentLibrary: React.FC<DocumentLibraryProps> = ({ documents, onRefresh }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Inspect Chunks Modal
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);
  const [chunks, setChunks] = useState<DocumentChunk[]>([]);
  const [isLoadingChunks, setIsLoadingChunks] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadMessage(null);
    setUploadError(null);

    try {
      const res = await api.uploadDocument(file);
      setUploadMessage(res.message);
      onRefresh();
    } catch (err: any) {
      setUploadError(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (doc: DocumentItem) => {
    if (!confirm(`Are you sure you want to delete '${doc.filename}' and remove it from the vector index?`)) return;
    try {
      await api.deleteDocument(doc.id);
      onRefresh();
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const handleInspectChunks = async (doc: DocumentItem) => {
    setSelectedDoc(doc);
    setIsLoadingChunks(true);
    try {
      const data = await api.getDocumentChunks(doc.id);
      setChunks(data);
    } catch (err: any) {
      alert(`Failed to load chunks: ${err.message}`);
    } finally {
      setIsLoadingChunks(false);
    }
  };

  const handleCreateSampleDocument = async () => {
    const sampleContent = `# Marie Curie: Life and Scientific Work

Marie Sklodowska Curie (7 November 1867 – 4 July 1934) was a Polish and naturalized-French physicist and chemist who conducted pioneering research on radioactivity. She was the first woman to win a Nobel Prize, the first person to win a Nobel Prize twice, and the only person to win a Nobel Prize in two scientific fields.

## Nobel Prizes
Curie won the 1903 Nobel Prize in Physics with her husband Pierre Curie and physicist Henri Becquerel for their pioneering work on radioactivity. In 1911, she was awarded the Nobel Prize in Chemistry for her discovery of the elements radium and polonium.

## Early Life
She was born in Warsaw, in the Kingdom of Poland, then part of the Russian Empire. She studied at Warsaw's clandestine Flying University and began her practical scientific training in Warsaw. In 1891, aged 24, she followed her elder sister Bronislawa to study in Paris, where she earned her higher degrees and conducted her subsequent scientific work.

## Discovery of Radium
In 1898, Marie and Pierre Curie discovered the radioactive elements polonium and radium after isolating them from uraninite ore. She died in 1934 of aplastic anemia caused by prolonged exposure to ionizing radiation.
`;

    const blob = new Blob([sampleContent], { type: 'text/markdown' });
    const file = new File([blob], 'marie_curie_biography.md', { type: 'text/markdown' });

    setIsUploading(true);
    try {
      const res = await api.uploadDocument(file);
      setUploadMessage(res.message);
      onRefresh();
    } catch (err: any) {
      setUploadError(err.message || 'Sample creation failed');
    } finally {
      setIsUploading(false);
    }
  };

  const filteredDocs = documents.filter(d => 
    d.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalChunksCount = documents.reduce((acc, d) => acc + d.total_chunks, 0);

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 sm:p-7 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-2xl">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-300 text-xs font-medium mb-2">
            <Sparkles className="w-3 h-3 text-violet-400" />
            <span>Document Ingestion & FAISS Index</span>
          </div>
          <h2 className="text-xl font-bold text-[#F4F4FA] flex items-center gap-2">
            <FolderGit2 className="w-5 h-5 text-violet-400" />
            Document Library & Vector Corpora
          </h2>
          <p className="text-xs text-[#94A3B8] mt-1 max-w-xl">
            Upload authoritative documents (.pdf, .txt, .md) to build the grounded knowledge base for verification.
          </p>
        </div>

        <button
          onClick={handleCreateSampleDocument}
          className="px-4 py-2.5 rounded-xl bg-[#080910] hover:bg-[#1a1d2d] border border-white/[0.08] text-xs font-semibold text-violet-300 transition-all flex items-center gap-1.5 cursor-pointer"
        >
          <FileText className="w-4 h-4 text-violet-400" />
          Load Benchmark Knowledge Base
        </button>
      </div>

      {/* Upload Dropzone */}
      <div className="p-8 sm:p-10 rounded-2xl bg-[#11131D]/80 border-2 border-dashed border-white/[0.1] hover:border-violet-500/40 transition-colors text-center backdrop-blur-md">
        <UploadCloud className="w-12 h-12 text-violet-400/80 mx-auto mb-3" />
        <h3 className="text-sm font-semibold text-[#F4F4FA]">
          Upload Reference Documents
        </h3>
        <p className="text-xs text-[#94A3B8] mt-1 mb-4">
          Supports text-based PDF (with page tracking), Markdown (.md), and plain text (.txt).
        </p>

        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept=".pdf,.txt,.md,.markdown"
          className="hidden"
        />

        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 disabled:from-slate-800 disabled:to-slate-800 text-white font-medium text-xs transition-all shadow-[0_0_16px_rgba(139,92,246,0.3)] inline-flex items-center gap-2 cursor-pointer"
        >
          {isUploading ? (
            <>
              <RotateCw className="w-4 h-4 animate-spin" />
              <span>Indexing document passages...</span>
            </>
          ) : (
            <>
              <UploadCloud className="w-4 h-4" />
              <span>Select File to Index</span>
            </>
          )}
        </button>

        {uploadMessage && (
          <div className="mt-4 flex items-center justify-center gap-2 text-xs text-emerald-300 bg-emerald-950/30 border border-emerald-500/30 p-2.5 rounded-xl max-w-md mx-auto">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
            <span>{uploadMessage}</span>
          </div>
        )}

        {uploadError && (
          <div className="mt-4 flex items-center justify-center gap-2 text-xs text-rose-300 bg-rose-950/30 border border-rose-500/30 p-2.5 rounded-xl max-w-md mx-auto">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{uploadError}</span>
          </div>
        )}
      </div>

      {/* Index Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 sm:p-5 rounded-2xl bg-[#11131D]/80 border border-white/[0.07]">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Total Indexed Documents</span>
          <div className="text-xl font-bold text-[#F4F4FA] mt-1">{documents.length}</div>
        </div>
        <div className="p-4 sm:p-5 rounded-2xl bg-[#11131D]/80 border border-white/[0.07]">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Total Chunks in FAISS Index</span>
          <div className="text-xl font-bold text-violet-300 mt-1">{totalChunksCount}</div>
        </div>
        <div className="p-4 sm:p-5 rounded-2xl bg-[#11131D]/80 border border-white/[0.07]">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Embedding Vector Dimension</span>
          <div className="text-xl font-bold text-blue-400 mt-1">384 (MiniLM-L6)</div>
        </div>
      </div>

      {/* Document Table */}
      <div className="p-6 rounded-2xl bg-[#11131D]/90 border border-white/[0.08] backdrop-blur-xl shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h3 className="text-base font-semibold text-[#F4F4FA]">
            Indexed Corpus Collection ({filteredDocs.length})
          </h3>
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-4 py-1.5 rounded-xl bg-[#080910] border border-white/[0.07] text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-violet-500/50"
            />
          </div>
        </div>

        {documents.length === 0 ? (
          <div className="text-center py-12 text-[#94A3B8] text-sm">
            Your document library is empty. Upload reference PDFs or text files to begin verification.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs uppercase bg-[#080910] text-slate-400 border-b border-white/[0.06]">
                <tr>
                  <th className="py-3 px-4">Document</th>
                  <th className="py-3 px-4">Format</th>
                  <th className="py-3 px-4">Pages</th>
                  <th className="py-3 px-4">Chunks</th>
                  <th className="py-3 px-4">File Size</th>
                  <th className="py-3 px-4">Indexed At</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.05]">
                {filteredDocs.map((doc) => (
                  <tr key={doc.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4 font-medium text-[#F4F4FA] flex items-center gap-2">
                      <FileIcon className="w-4 h-4 text-violet-400 shrink-0" />
                      <span className="truncate max-w-xs">{doc.filename}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-[#080910] text-slate-300 border border-white/[0.06]">
                        {doc.file_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono">{doc.total_pages}</td>
                    <td className="py-3.5 px-4 text-xs font-mono text-violet-300 font-semibold">
                      {doc.total_chunks}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono text-slate-400">
                      {(doc.file_size / 1024).toFixed(1)} KB
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3.5 px-4 text-right space-x-2">
                      <button
                        onClick={() => handleInspectChunks(doc)}
                        className="px-2.5 py-1 rounded-lg bg-[#080910] hover:bg-violet-600/20 text-xs font-medium text-slate-200 border border-white/[0.08] hover:border-violet-500/40 transition-all inline-flex items-center gap-1 cursor-pointer"
                        title="View chunks"
                      >
                        <Eye className="w-3.5 h-3.5" /> Chunks
                      </button>
                      <button
                        onClick={() => handleDelete(doc)}
                        className="p-1 rounded-lg hover:bg-rose-950/40 text-slate-400 hover:text-rose-400 transition-colors cursor-pointer"
                        title="Delete document"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Inspect Chunks Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="bg-[#11131D] border border-white/[0.1] rounded-2xl max-w-3xl w-full max-h-[80vh] flex flex-col shadow-2xl">
            <div className="p-5 border-b border-white/[0.06] flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-[#F4F4FA] flex items-center gap-2">
                  <Layers className="w-4 h-4 text-violet-400" />
                  Indexed Chunks: {selectedDoc.filename}
                </h3>
                <p className="text-xs text-[#94A3B8] mt-0.5">
                  Showing {chunks.length} extracted passages with character offsets and page references.
                </p>
              </div>
              <button
                onClick={() => setSelectedDoc(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-white/[0.06] transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-5 overflow-y-auto space-y-3 flex-1">
              {isLoadingChunks ? (
                <div className="text-center py-8 text-slate-400 text-sm">
                  Loading passages...
                </div>
              ) : chunks.length === 0 ? (
                <div className="text-center py-8 text-slate-500 text-sm">
                  No chunks found for this document.
                </div>
              ) : (
                chunks.map((c) => (
                  <div key={c.id} className="p-3.5 rounded-xl bg-[#080910] border border-white/[0.06] text-xs space-y-1.5">
                    <div className="flex items-center justify-between text-[11px] text-slate-400">
                      <span className="font-semibold text-slate-300">
                        Chunk #{c.chunk_index + 1} {c.page_number ? `• Page ${c.page_number}` : ''}
                      </span>
                      <span className="font-mono text-slate-500">
                        Chars: [{c.start_char} - {c.end_char}] • ~{c.token_count} tokens
                      </span>
                    </div>
                    <p className="text-slate-200 leading-relaxed bg-[#11131D]/80 p-2.5 rounded-lg border border-white/[0.05]">
                      {c.content}
                    </p>
                  </div>
                ))
              )}
            </div>

            <div className="p-4 border-t border-white/[0.06] text-right">
              <button
                onClick={() => setSelectedDoc(null)}
                className="px-4 py-2 rounded-xl bg-[#080910] hover:bg-white/[0.06] text-slate-200 text-xs font-semibold border border-white/[0.08] transition-colors cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
