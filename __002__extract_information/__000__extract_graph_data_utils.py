import json
import os
from typing import Literal, Optional, Union, List

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from tqdm import tqdm

from common.llm import my_llm
from common.path_utils import get_file_path

# ======================
# 枚举定义
# ======================
EntityType = Literal["Symptom", "Disease", "Formula", "Herb", "Effect", "Source"]

RelationType = Literal[
    "TREATS_DISEASE",
    "ALLEVIATES_SYMPTOM",
    "HAS_EFFECT",
    "HAS_INGREDIENT",
    "HAS_SYMPTOM",
    "FROM_SOURCE"
]


# ======================
# 属性定义
# ======================
class FormulaAttributes(BaseModel):
    alias: Optional[str] = Field(default=None, description="方剂别名")
    effect: Optional[str] = Field(default=None, description="方剂功效")
    indication: Optional[str] = Field(default=None, description="方剂主治")
    taboo: Optional[str] = Field(default=None, description="方剂禁忌")
    usage: Optional[str] = Field(default=None, description="方剂用法用量")


class HerbAttributes(BaseModel):
    dosage: Optional[str] = Field(default=None, description="药材用法用量")
    effect: Optional[str] = Field(default=None, description="药材功效")
    indication: Optional[str] = Field(default=None, description="药材主治")
    meridian: Optional[str] = Field(default=None, description="药材归经")
    origin: Optional[str] = Field(default=None, description="药材来源")
    place: Optional[str] = Field(default=None, description="药材产地或生境分布")
    processing: Optional[str] = Field(default=None, description="药材炮制方法")
    property_flavor: Optional[str] = Field(default=None, description="药材性味")
    taboo: Optional[str] = Field(default=None, description="药材禁忌")
    traits: Optional[str] = Field(default=None, description="药材性状特征")


# ======================
# 实体与关系结构
# ======================
class Entity(BaseModel):
    name: str = Field(description="实体名称")
    type: EntityType = Field(description="实体类型（只能从给定集合中选择）")
    attributes: Optional[Union[FormulaAttributes, HerbAttributes]] = Field(
        default=None, description="实体属性，方剂使用 FormulaAttributes，药材使用 HerbAttributes"
    )


class Relation(BaseModel):
    subject: str = Field(description="关系主体实体名称")
    subject_type: EntityType = Field(description="关系主体实体类型（只能从给定集合中选择）")
    relation: RelationType = Field(description="关系类型（只能从给定集合中选择）")
    object: str = Field(description="关系客体实体名称")
    object_type: EntityType = Field(description="关系客体实体类型（只能从给定集合中选择）")


class TCMKnowledgeGraph(BaseModel):
    entities: List[Entity] = Field(description="抽取的实体列表")
    relations: List[Relation] = Field(description="抽取的实体关系列表")


# 初始化解析器
parser = JsonOutputParser(pydantic_object=TCMKnowledgeGraph)

"""
{
    "entities":[{
        "name": "三圣散",
        "type": "Formula",
        "attributes": {
            "alias": "三圣散别名",
            "effect": "三圣散功效",
            "indication": "三圣散主治",
            "taboo": "三圣散禁忌",
            "usage": "三圣散用法用量"
        }
    }, {
        "name": "人参",
        "type": "Herb",
        "attributes": {
            "dosage": "人参用法用量",
            "effect": "人参功效",
            "indication": "人参主治",
            "meridian": "人参归经",
            "origin": "人参来源",
            "place": "人参产地或生境分布",
            "processing": "人参炮制方法",
            "property_flavor": "人参性味",
            "taboo": "人参禁忌",
            "traits": "人参性状特征"
        }
    }],
    "relations":[{
            "subject": "三圣散",
            "subject_type": "Formula",
            "relation": "TREATS_DISEASE",
            "object": "感冒",
            "object_type": "Disease"
        }, {}]
    ]
}

"""


# 定义 Prompt
prompt = PromptTemplate(
    template=(
        "你是一个中医知识图谱抽取专家。请从以下文本中提取结构化知识：\n"
        "仅当文本中存在实体之间的明确关系时（如‘某方剂治疗某疾病’、‘某药材具有某功效’、‘方剂包含药材’等），才进行抽取。\n"
        "如果文本中仅描述单个实体的信息、未涉及其他实体或关系，请不要抽取，返回空结构：\n"
        "{{\"entities\": [], \"relations\": []}}\n\n"

        "【实体类型说明】\n"
        "- Symptom：症状，如咳嗽、腹痛等\n"
        "- Disease：疾病，如感冒、肺炎、肾虚等\n"
        "- Formula：方剂，如四君子汤、桂枝汤等\n"
        "- Herb：药材，如人参、黄芪、丁香等\n"
        "- Effect：功效，如补气、活血、祛湿、止痛等\n"
        "- Source：出处，如《本草纲目》《伤寒论》等\n\n"

        "【关系类型说明】\n"
        "- TREATS_DISEASE：方剂或药材治疗某种疾病\n"
        "- ALLEVIATES_SYMPTOM：方剂或药材缓解某种症状\n"
        "- HAS_EFFECT：方剂或药材具有某种功效\n"
        "- HAS_INGREDIENT：方剂包含某种药材\n"
        "- HAS_SYMPTOM：疾病包含某种症状\n"
        "- FROM_SOURCE：方剂出自某文献或出处\n\n"

        "若文本涉及方剂或药材，请补充对应的属性字段（如功效、性味、剂量等）。\n"
        "如果文本主要是讲方剂的，请不要抽取药材的属性字段。\n"
        "如果文本主要是讲药材的，请不要抽取方剂的属性字段。\n"
        "如果值为空null，则不必显示键的值。"
        "所有输出必须严格符合以下 JSON 格式：\n"
        "{format_instructions}\n\n"
        "输入文本：{text}"
    ),
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# ======================
# 主函数封装
# ======================
def extract_tcm_knowledge(text: str):
    # 构建抽取链
    chain = prompt | my_llm | parser
    return chain.invoke({"text": text})


def extract_formula_graph(formula_dir, output_path, resume=True):
    """依次读取方剂 txt，抽取实体和关系，写入同一个 JSON。"""
    done = {}
    if resume and os.path.exists(output_path):
        with open(output_path, encoding="utf-8") as f:
            for item in json.load(f):
                done[item["name"]] = item

    files = sorted(name for name in os.listdir(formula_dir) if name.endswith(".txt"))
    for filename in tqdm(files, desc="抽取方剂"):
        name = filename[:-4]
        if name in done:
            continue
        with open(os.path.join(formula_dir, filename), encoding="utf-8") as f:
            text = f.read().strip()
        if not text:
            continue
        try:
            data = extract_tcm_knowledge(text)
        except Exception as e:
            tqdm.write(f"失败 {name}: {e}")
            continue
        done[name] = {
            "name": name,
            "entities": data.get("entities", []),
            "relations": data.get("relations", []),
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(list(done.values()), f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(done)} 条到 {output_path}")


if __name__ == "__main__":
    extract_formula_graph(
        formula_dir=get_file_path("__001__clawler/方剂"),
        output_path=get_file_path("__002__extract_information/formula_graph.json"),
    )