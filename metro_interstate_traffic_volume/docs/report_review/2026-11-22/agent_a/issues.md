# Vấn đề và giới hạn kiểm tra báo cáo

## A-I001 (P2) — missing citation

P0026. CHƯA XÁC MINH NGUỒN.

Con số49giờ không có nguồn/năm/phạm vi; câu viết gộp và lỗi 'mất trung'.

Đề xuất: Bỏ số49giờ khi chưa có nguồn; mở đầu bằng nhu cầu ước lượng lưu lượng theo giờ ở trạm đang xét.

## A-I002 (P1) — research design

P0027, P0028, P0031, P0032, P0035. XÁC MINH TỪ BÁO CÁO.

Mục1.2 chỉ liệt kê mục tiêu, chưa định danh câu hỏi nghiên cứu; đánh số nhảy từ1.2 đến1.4. Từ 'ảnh hưởng' dễ bị đọc thành nhân quả.

Đề xuất: Thêm RQ rõ phạm vi: quy luật thời gian/lễ, giá trị bổ sung Weather/History trong matchedCV, mô hình/ensemble và sai số; sửa sốmục.

## A-I003 (P2) — missing sections

P0035, P0036. XÁC MINH TỪ BÁO CÁO.

1.4 và1.5 chỉ có tiêu đề; Chương2 ghi nghiên cứu liên quan nhưng chưa có khảo sát nghiên cứu/citation.

Đề xuất: Viết tổng quan dữ liệu và nghiên cứu liên quan có nguồn; mô tả bố cục đã thực hiện, không buộc phải tìm một paper duy nhất.

## A-I004 (P1) — theory scope

P0060, P0062. XÁC MINH TỪ BÁO CÁO.

OOB được mô tả như không cầnvalidation riêng, dễ hiểu thành đã dùngOOB thay đánh giá theo thời gian. 'Gần như không tăng độchệch' không phải bảo đảm.

Đề xuất: Nêu đây là nguyên lý chung RF; dự án dùng CV theo thời gian vàvalidation, không dùngOOB thay thế. Trình bày lợi ích giảm phương sai có điều kiện.

## A-I005 (P2) — formula QA

P0055, P0056, P0058, P0059, P0061, P0064, P0065, P0068, P0069, P0071, P0073. CHƯA XÁC MINH 28 CÔNG THỨC NATIVE.

28 nodephươngtrình native API chỉ trảequation={} nên chưa nhìn được ký hiệu. Không được kết luận côngthức bị thiếu/sai trongDocs.

Đề xuất: Kiểm côngthức bằng bảnPDF/render hoặc xem trực tiếp ởDocs; đây là giới hạn tríchxuất, không là lỗi đã xác minh.

## A-I006 (P3) — formula QA

P0076, P0077, P0078. XÁC MINH TỪ BÁO CÁO.

3 ảnh MAE/RMSE/R² được xem; côngthức hiển thị phù hợp định nghĩa e_i; không phát hiện lỗi ở ảnh.

Đề xuất: Giữ; thêm định nghĩa n và quy tắcclip dự đoán trong phần thực nghiệm.

## A-I007 (P3) — formula QA

P0071, P0072. XÁC MINH TỪ BÁO CÁO.

2 ảnh objectiveOmega vàgain cógamma đã xem, không thấy lỗi côngthức; kýhiệunative xung quanhchưa kiểm.

Đề xuất: Giữ ảnh, bổ sungcitation tài liệuXGBoost và tên tham số thực dùng.

## A-I008 (P1) — reproducibility

P0080. XÁC MINH TỪ BÁO CÁO.

Claimclipnegative cần kiểm mọi đườngscore; primarymetric vẫn chỉ là lời nhắc nêu rõ, chưachốtMAE.

Đề xuất: GhiMAE làtiêu chíselection;RMSE/R² làbổ sung; gắnscorehelper và xác minhclipđồngnhất.

## A-I009 (P2) — reproducibility

P0083. XÁC MINH TỪ BÁO CÁO.

Caveatfold khácđộdàilịchđúnghướng nhưng chưa có foldmanifest/start/end/n thực trong3.6.

Đề xuất: Thêm bảngcohort/fold1..3, ntrain/nscore,mốclịch,hash/runID.

## A-I010 (P2) — provenance

P0087, P0088. XÁC MINH TỪ BÁO CÁO.

NguồnUCI mới ghi 'Nguồn: UCI', mục tài liệuthamkhảo chưa cólink/DOI/ngàytruycập; sốCSV khácmô tảnguồn cầntruyvết.

Đề xuất: TríchUCI DOI10.24432/C5X60B; nối sốkiểm riêng với notebookEDA_general vàđầu ra hiệncó.

## A-I011 (P1) — missing method

P0170, P0289, P0290, P0291, P0292, P0293. XÁC MINH TỪ BÁO CÁO.

Câu 'Cácvấnđềtrênđượcxửlýtạimục3.3' trỏ đến mục vẫn '[Nhóm bổ sung]'.

Đề xuất: Điền quytrình làm sạch từsource thật,phânbiệt sửa giátrịbấthợp lý,aggregateuniquehour,missinggrid,khôngbịa quytrình.

## A-I012 (P1) — scope

P0172, P0202. XÁC MINH TỪ BÁO CÁO.

EDA toàn40575giờ bao gồm miềnvalidation/test theo thời gian; báo cáo chưa nói nóchỉmôtả hay đượcdùngchọnfeature.

Đề xuất: Ghi rõdescriptiveEDA toànCSV; mọiquyếtđịnh/tuning dùngtrain. Nếu EDAwholedata đã ảnhhưởngselection, côngkhai hạnchế.

## A-I013 (P2) — figure reproducibility

P0198, P0199, P0206, P0239, P0269. XÁC MINH TỪ BÁO CÁO.

4 hìnhEDAđãxem khớpmôtả; ảnh không ghi tổngn/nguồn,file/hàm sinh hoặcperiod; hình3.4 hiểnnhiềunhãnnhưng chỉbảngcho một sốnhóm.

Đề xuất: Thêmchúthíchscope40575uniquehours,nguồnnotebook/hìnhgốc;nnhómđầyđủhoặc chỉ rõnởbảngphụlục.

## A-I014 (P3) — table labeling

P0211, P0272, P0274. XÁC MINH TỪ BÁO CÁO.

Header 'giờ/Giờ' dùng để chỉsốmẫu cóthểnhầm với biến giờtrongngày.

Đề xuất: Đổi thành'n (giờquantrắc)' vàthốngnhất chữhoa/đơnvị.

## A-I015 (P2) — method precision

P0243. XÁC MINH TỪ BÁO CÁO.

Median cácgiátrịphânbiệt làquytắckhác mediantrêntấtcảdòng; chưanêuvìsaođểtránhweatherlabels lặplàmtrọngsố.

Đề xuất: Nêu rõ dedupgiátrịtrongtừngtimestamp/cộtsố rồimedian; dẫn hàmsource; khôngápsangtarget.

## A-I016 (P1) — missing analysis

P0032, P0240. XÁC MINH TỪ BÁO CÁO.

Mụctiêungàylễso cùngthứchưacókếtquảngàylễ ở3.2; chưađốichiếu cùnggiờvànnhóm.

Đề xuất: Thêm EDAngàylễmatchedweekday-hour,nvàCI; nếu chưađủsource ghi chưahoànthành.

## A-I017 (P1) — missing method

P0294, P0295, P0296, P0297, P0298, P0299. XÁC MINH TỪ BÁO CÁO.

Encoding/scaling và Time/Weather/History còn toàn gợiý, khôngcóA12/B27/C30/danhsáchcộtcôngthức.

Đề xuất: Điền bảngconfig thực,lagsđúngtimestamp vàmean24h loại giờt; trainfitimputation/scaler;Ridgeweekday_hour nếu có.

## A-I018 (P1) — pipeline ambiguity

P0301. XÁC MINH TỪ BÁO CÁO.

Sơđồgợiý đặt featuretrướcsplit cóthể bịhiểufitpreprocessing trênfullCSV; chuỗi này chưa phải kiếntrúc đãthựcthi.

Đề xuất: Vẽ2lớp:clean/aggregate deterministic và foldtrainfittransform; causalhistory chỉquansáttrướct.

## A-I019 (P1) — missing experiment protocol

P0304, P0305, P0306, P0307, P0308, P0309, P0310, P0311, P0312, P0313, P0314, P0315, P0316, P0317. XÁC MINH TỪ BÁO CÁO.

Toànbộ3.6 thiếu chia70/15/15/cohort/fold/searchbudget/baseline/FEprotocol; bađoạnOOF không bù đượcthiếu này.

Đề xuất: Điền từmanifest/code/log, tách5FEconfig và3tuningconfig vàensemble20–22Nov; khônggộp protocolkhácnhau.

## A-I020 (P1) — stale architecture

P0318, P0319. XÁC MINH TỪ BÁO CÁO.

OOFensemble chỉ nêuRF+XGB; khôngcóExtraTrees/mốc22Nov hoặc cấu hìnhtrọngsốfinal.

Đề xuất: Gắnđoạn2modelvớithửnghiệm20–21Nov; thêmfinal3modelRF25/XGB25/ExtraTrees50 từmanifest,đánhgiávalđãxemnhiềulần.

## A-I021 (P1) — selection bias

P0319, P0320. XÁC MINH TỪ BÁO CÁO.

BáocáođãnhắcOOFweightscore khôngđộclập nhưng chưanhắctuning vàcải tiếnnhiềulần trêncùngvalidation.

Đề xuất: PhânbiệtOOFselection,exploratoryvalidationvàuntouchedtest;khônggọi190.19làtesthoặcbằngchứngcuốicùng.

## A-I022 (P1) — missing reproducibility

P0323, P0324, P0325. XÁC MINH TỪ BÁO CÁO.

Môitrường/seed/runIDvẫntrống.

Đề xuất: Điền version từsavedmetadata/environment;đừngnêu phầncứngkhôngcóbằngchứng; chỉđườngdẫnrun/cấu hình.

## A-I023 (P1) — missing results

P0326, P0327, P0328, P0329, P0330. XÁC MINH TỪ BÁO CÁO.

Khôngcóbaseline,tuning,bestparams hoặcmetricsmodel trongCh4.

Đề xuất: Thêm matchedCVvàvalidationtừnggiaiđoạn từCSV, ghi n/start/end; khôngđồngnhấtCV247.9vàvalidation190.19.

## A-I024 (P1) — unfinished test

P0331, P0332, P0338, P0343, P0348. XÁC MINH TỪ BÁO CÁO.

Mục4.4 vàbảngtestlàtemplate,trống; khônglàkhẳngđịnhđãtest. 'So sánhcácmôhình trên test' căngvới 'chỉtestmôhìnhđãchốt'.

Đề xuất: Đổi4.4thành so sánhvalidationthựctế;testriêng chờfinalfreeze/refit. Nếu giữ bảngtest chưachạy ghi chưathựchiện,khôngđiềnvalidationvào.

## A-I025 (P1) — missing analysis

P0353, P0354, P0355, P0356, P0357, P0358, P0359, P0360, P0361, P0362, P0363, P0364, P0365, P0366. XÁC MINH TỪ BÁO CÁO.

Over/underfit,saisố,importance,ablation,trảlờiRQđềutrống.

Đề xuất: Chỉthêmphântíchđãcósourcereproducible;phânbiệtlỗitheogiờ/lễ/weather/gapsvàimportancekhôngnhânquả.

## A-I026 (P1) — missing conclusion

P0369, P0370, P0371, P0372, P0373, P0374, P0375. XÁC MINH TỪ BÁO CÁO.

Ch5chưacókếtluận/hạnchế/môhìnhđãchọn.

Đề xuất: Nêumôhìnhspecđãchốt,refitchưaxong/testchưachạy nếumanifestcònđúng;hạnchế3fold/gaps/DST/weatheravailability/validationreuse.

## A-I027 (P2) — provenance and authorship

P0017, P0018, P0377, P0378, P0380, P0381, P0382, P0383, P0384, P0385, P0406, P0407, P0408. XÁC MINH TỪ BÁO CÁO.

Camkếthọcthuật,tàiliệuthamkhảo,danhmụcmã/log,phâncôngvàchecklist cònplaceholder.

Đề xuất: Điềnnguồndữliệu,algorithm/library vàAI thực dùng;runids/phâncôngcóbằngchứng;khôngtựgánngườithựchiện.

## A-I028 (P3) — copyediting

P0122, P0125, P0131, P0136, P0139, P0160. XÁC MINH TỪ BÁO CÁO.

Lỗichính tả/spacing: 'kếtquảtra','Null,Giátrịnull','lăpk','timestamo','weather _description','dương..'.

Đề xuất: Sửa nhẹgiữ nguyên ý/số; khôngthay cộtcodeweather_description.
