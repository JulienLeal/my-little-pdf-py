# 🏰 Magic Kingdom Guide - PDF Example

Este diretório contém um exemplo completo de geração de PDF usando nossa engine markdown-to-pdf. O exemplo demonstra como criar um guia de viagem profissional com componentes customizados.

## 📄 Arquivos do Exemplo

### Entrada
- **`magic_kingdom_guide.md`** - Guia completo do Magic Kingdom (1,125 palavras, 119 linhas)
- **`magic_kingdom_colorful.yaml`** - Tema customizado Disney com cores vibrantes

### Saída - Diferentes Versões
- **`magic_kingdom_guide.pdf`** - PDF com tema minimal (122KB, preto e branco)
- **`magic_kingdom_guide_colorful.pdf`** - PDF com gradientes CSS (135KB, pode ter problemas com cores)
- **`magic_kingdom_guide_weasyprint_optimized.pdf`** - PDF otimizado com cores sólidas (133KB, **RECOMENDADO**)

### Scripts
- **`generate_magic_kingdom_guide.py`** - Script básico
- **`generate_magic_kingdom_guide_colorful.py`** - Script que gera múltiplas versões

## 🎨 Problema de Cores & Solução

### ❌ Problema Identificado
O WeasyPrint (engine de PDF) tem limitações com gradientes CSS complexos, resultando em componentes que ficam preto e branco no PDF final, mesmo que o CSS contenha cores vibrantes.

### ✅ Solução Implementada
Criamos uma versão otimizada do CSS dos componentes (`components_weasyprint.css`) que usa:
- **Cores sólidas** em vez de gradientes
- **Otimizações específicas** para WeasyPrint
- **Seção @media print** com regras !important

### 🎪 Comparação de Versões

| Versão | Tamanho | Componentes | Cores | Recomendação |
|--------|---------|-------------|-------|--------------|
| **Minimal** | 122KB | ✅ | ❌ Preto/branco | Documentos simples |
| **Colorful** | 135KB | ✅ | ⚠️ Podem não aparecer | Para testes de CSS |
| **Optimized** | 133KB | ✅ | ✅ **Cores sólidas vibrantes** | **🎯 USAR ESTA** |

## 🚀 Como Executar

### Opção 1: Versão Otimizada (Recomendada)
```bash
python -c "import sys; sys.path.insert(0, 'src'); from md_to_pdf.cli import MarkdownToPDFCLI; cli = MarkdownToPDFCLI(); cli.run(['examples/magic_kingdom_guide.md', '--output', 'examples/magic_kingdom_guide_otimizado.pdf', '--theme', 'examples/magic_kingdom_colorful.yaml', '--title', 'Magic Kingdom - Guia Colorido'])"
```

### Opção 2: Script Automatizado (Gera Múltiplas Versões)
```bash
python examples/generate_magic_kingdom_guide_colorful.py
```

### Opção 3: CLI Manual
```bash
# Geração básica
python -m md_to_pdf examples/magic_kingdom_guide.md

# Com tema colorido
python -m md_to_pdf examples/magic_kingdom_guide.md \
  --theme examples/magic_kingdom_colorful.yaml \
  --output examples/magic_kingdom_guide_colorido.pdf \
  --title "Magic Kingdom - Guia Completo do Dia 1"
```

## ✨ Recursos Demonstrados

### 🎪 Componentes Customizados com Cores
O exemplo utiliza todos os componentes customizados da nossa engine **COM CORES VIBRANTES**:

#### 🔮 Magic Secret (magic_secret)
- **Fundo**: Azul royal (#3f51b5)
- **Borda**: Azul escuro (#1a237e)
- **Texto**: Branco com fundo semi-transparente

```markdown
:::magic_secret title="SEGREDINHO MÁGICO"
Mesmo que o parque abra às 9h, você pode entrar na Main Street às 8h!
:::
```

#### 💡 Tip Box (tip_box)
- **Fundo**: Azul claro (#e3f2fd)
- **Borda**: Azul (#2196f3)
- **Texto**: Azul escuro (#1565c0)

```markdown
:::tip_box title="🎯 Ordem Sugerida do Parque" color="blue"
**Liberty Square** → **Adventureland** → **Frontierland**
:::
```

#### ⚠️ Attention Box (attention_box)
- **Fundo**: Amarelo claro (#fff8e1)
- **Borda esquerda**: Laranja (#ff9800)
- **Texto**: Laranja escuro (#bf360c)

```markdown
:::attention_box title="CRONOMETRANDO A MAGIA" type="warning"
Essa jornada leva uns 30 minutinhos. Então saia 1 hora antes!
:::
```

### 📝 Elementos Markdown Coloridos
- **Títulos**: Cores hierárquicas (roxo, coral, turquesa)
- **Texto enfatizado**: Vermelho brilhante para **negrito**, roxo para *itálico*
- **Links e separadores**: Estilizados com cores temáticas

## 🛠️ Solução Técnica

### Problema dos Gradientes CSS
```css
/* ❌ NÃO FUNCIONA no WeasyPrint */
.magic-secret {
    background: linear-gradient(135deg, #1a237e 0%, #3f51b5 100%);
}

/* ✅ FUNCIONA no WeasyPrint */
.magic-secret {
    background-color: #3f51b5;
    border: 3px solid #1a237e;
}
```

### Otimizações Aplicadas
1. **Cores sólidas** em vez de gradientes
2. **Bordas coloridas** para destaque visual
3. **Regras @media print** com !important
4. **Box-shadow removido** no modo print
5. **Cores contrastantes** para legibilidade

## 📊 Estatísticas do Exemplo

| Métrica | Valor |
|---------|-------|
| **Tamanho do arquivo MD** | 6.748 caracteres |
| **Número de palavras** | 1.125 palavras |
| **Número de linhas** | 119 linhas |
| **PDF otimizado** | 133.058 bytes (130 KB) |
| **Tempo de geração** | ~0.42 segundos |
| **Componentes coloridos** | 8 instâncias funcionando |

## 🎯 Benefícios da Versão Otimizada

### Para Desenvolvedores
- ✅ **Cores funcionam** corretamente no PDF
- ✅ **CSS compatível** com WeasyPrint
- ✅ **Performance otimizada** para geração de PDF
- ✅ **Manutenibilidade** simples

### Para Usuários Finais
- ✅ **Visual atrativo** com cores vibrantes
- ✅ **Componentes destacados** visualmente
- ✅ **Legibilidade excelente** com contraste adequado
- ✅ **PDF pronto para impressão** colorida

## 🔧 Personalização

### Modificar Cores dos Componentes
Edite `assets/css/components.css`:
```css
.magic-secret {
    background-color: #sua-cor-preferida;
    border: 3px solid #sua-borda-preferida;
}
```

### Criar Novos Temas Coloridos
```yaml
# Seu tema personalizado
styles:
  h1:
    color: "#sua-cor-h1"
  h2:
    color: "#sua-cor-h2"
```

## 🐛 Solução de Problemas

### Componentes ainda aparecem sem cor?
1. ✅ Verifique se está usando `magic_kingdom_guide_weasyprint_optimized.pdf`
2. ✅ Confirme que o tema `magic_kingdom_colorful.yaml` está sendo aplicado
3. ✅ Execute: `--validate --theme examples/magic_kingdom_colorful.yaml`

### PDF muito pesado?
- Use tema `minimal.yaml` para versão mais leve
- A diferença de tamanho indica que as cores estão sendo aplicadas

### Gradientes não funcionam?
- **Isso é normal** no WeasyPrint
- Use nossa versão otimizada com cores sólidas
- O resultado visual é igualmente atrativo

## 🚀 Próximos Passos

1. **✅ Use a versão otimizada** sempre que quiser cores
2. **Experimente diferentes temas** coloridos disponíveis
3. **Crie seus próprios componentes** coloridos
4. **Adapte as cores** para sua marca/tema
5. **Compartilhe PDFs coloridos** profissionais!

---

**🎪 Divirta-se criando PDFs coloridos e profissionais! ✨** 

*Versão otimizada testada e aprovada para produção! 🏆* 