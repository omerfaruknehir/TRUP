from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline,
    AutoModelForQuestionAnswering,
)
import torch
import langid

if torch.cuda.is_available():
    cuda_device = torch.tensor([1.2, 3], device='cuda')
    torch.set_default_device(cuda_device.device)
    print("Server will use the GPU:", torch.cuda.get_device_name(0))
else:
    print("No GPU available, using the CPU instead.")
    device = torch.device("cpu")

from infrastructure.decorators import type_check
from infrastructure.localization import Language

class NLPmodel:
    qa_model = AutoModelForQuestionAnswering.from_pretrained(
        "savasy/bert-base-turkish-squad"
    )
    qa_tokenizer = AutoTokenizer.from_pretrained(
        "savasy/bert-base-turkish-squad", do_lower_case=True
    )
    qa_nlp = pipeline("question-answering", model=qa_model, tokenizer=qa_tokenizer)

    sa_nlp = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment", device=0)

    # TODO: add language support
    @type_check
    def checklanguage(text: str):
        return langid.classify(text)

    @type_check
    def ispositive(text: str, lang: Language = "tr"):
        
        return NLPmodel.sa_nlp(text)[
            0
        ]  # ["label"] == "positive"

    @type_check
    def askfor(question: str, context: str, lang: Language = "tr"):
        return NLPmodel.qa_nlp(
            question=question, context=context
        )

    @type_check
    def spellcorrect(text: str, lang: Language = "tr"):
        return " "#.join(trnlp.auto_correct(trnlp.list_words(text)))


if __name__ == "__main__":
    model = NLPmodel()

    said = """
    İshak Ağa Çeşmesi, Onçeşmeler, On Çeşmeler, Beykoz Çeşmesi, Behruz Ağa Çeşmesi ya da I. Mahmud Çeşmesi; İstanbul'un Beykoz ilçesindeki bir çeşmedir. I. Süleyman'ın has odabaşı olarak görev yapan Behruz Ağa (ö. 1562/1563) tarafından, daha önceleri bir Bizans çeşmesinin bulunduğu alana yaptırıldı. Zamanla harap hâle gelen ve suyu akmayan çeşme, Temmuz 1746'da başlayan ve 1746 ya da 1747 yılında tamamlanan çalışmalar sonucunda İstanbul Gümrük Emini İshak Ağa tarafından yenilendi. İnşa edildiği dönemde bir mesire alanında yer alırken bölgede yapılaşmanın artmasıyla şehir dokusu içinde kaldı. 1948 öncesinde üç; 1948-1950, 1986, 2005-2006 ve 2016-2017 yıllarında ise birer kez olmak üzere toplamda yedi kez onarımdan geçti. Yapılan değişikliklerle kemerleri, üst örtüsü ve yan cephelerinde değişiklikler meydana gelirken kalemişi süslemeler eklendi. 1972'den beri korunması gereken tarihî eser statüsünde olan çeşme, Vakıflar Genel Müdürlüğü mülkiyetinde olup günümüzde işlevseldir.

    İshak Ağa Çeşmesi, Merkez Mahallesi'nde konumlanan bir meydan çeşmesi niteliğindedir. Kesme taştan inşa edilen kare planlı yapının zemini, ön yüz kaplaması ve sütunları mermerdendir. Arka kısmında, taş ve tuğladan oluşturulan duvarlarla çevrili haznesi yer alır. Üç cephesi ile iç kısmında yer alan sütunlar, birbirlerine çift merkezli teğet kemerlerle bağlanır. Sütun başlarının üzerinde bulunan kemerler ile yapıyı örten kırma çatı betonarmedir. Yapının tavan ve kemerlerin içe bakan kısımlarında kalemişi süslemeler yer alır. Ön yüzünde bulunan on bronz lüleden kesintisiz olarak su akar. Diğerlerinden daha büyük boyuttaki ortadaki iki lüle, dilimli bir kaş kemere sahip sağır bir niş şeklindeki aynataşı içindedir. Aynataşının üzerinde, 1746 ya da 1747'deki onarıma dair tek satırlık bir kitâbesi bulunur. Mermer bir tekneye akan suyun taşan kısmı, döşemeye oyulmuş kanaldan geçerek denize akar. Yapı, klasik Osmanlı mimarisi ile Barok mimari öğeleri taşır.
    """
    print(NLPmodel.askfor(question="Kaç kere onarımdan geçti?", context=said))

    print(NLPmodel.ispositive("kou oyun"))