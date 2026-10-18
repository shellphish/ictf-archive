import openai
import re
import time

import numpy as np

from tqdm import tqdm
from datasets import load_dataset
from tenacity import retry, stop_after_attempt, wait_chain, wait_fixed
from task import prompt_engineering


@retry(wait=wait_chain(*[wait_fixed(3) for i in range(3)] +
                       [wait_fixed(5) for i in range(2)] +
                       [wait_fixed(10)]))
def completion_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)


def test_answer(pred_str, ans_str):
    pattern = '\d*\.?\d+'
    pred = re.findall(pattern, pred_str)
    if (len(pred) >= 1):
        pred = pred[-1]
        gold = re.findall(pattern, ans_str)
        gold = gold[-1]
        return pred == gold
    else:
        return False


def parse_pred_ans(filename):
    with open(filename) as fd:
        lines = fd.readlines()
    am, a = None, None
    num_q, acc = 0, 0
    current_mode = 'none'
    questions = []
    ans_pred = []
    ans_gold = []
    for l in lines:
        if (l.startswith('Q: ')):
            if (am is not None and a is not None):
                questions.append(q)
                ans_pred.append(am)
                ans_gold.append(a)
                if (test_answer(am, a)):
                    acc += 1
            current_mode = 'q'
            q = l
            num_q += 1
        elif (l.startswith('A_model:')):
            current_mode = 'am'
            am = l
        elif (l.startswith('A:')):
            current_mode = 'a'
            a = l
        else:
            if (current_mode == 'q'):
                q += l
            elif (current_mode == 'am'):
                am += l
            elif (current_mode == 'a'):
                a += l
            else:
                raise ValueError(current_mode)

    questions.append(q)
    ans_pred.append(am)
    ans_gold.append(a)
    if (test_answer(am, a)):
        acc += 1
    print('num_q %d correct %d ratio %.4f' % (num_q, acc, float(acc / num_q)))
    return float(acc / num_q), questions, ans_pred, ans_gold


def test_finished(ans_model):
    if ('answer is' in ans_model):
        return True
    else:
        return False


def extract_ans(ans_model):
    ans_model = ans_model.split('\n')
    ans = []
    residual = []
    for li, al in enumerate(ans_model):
        ans.append(al)
        if ('answer is' in al):
            break
    residual = list(ans_model[li + 1:])
    ans = '\n'.join(ans)
    residual = '\n'.join(residual)
    return ans, residual


if __name__ == '__main__':

    # OpenAI API key
    openai.api_key = ""

    # Load in data
    gsm8k = load_dataset('gsm8k', 'main')
    validation_index = np.load('validation_index.npy')
    validation_data = gsm8k['train'].select(validation_index)
    gsm8k_test = gsm8k['test'][:100]       # test data (1319 samples in total, sample the first 100)

    i = 0
    with open('outputs1.txt', 'w') as fd:
        for q, a in tqdm(zip(gsm8k_test['question'], gsm8k_test['answer']),
                         total=len(gsm8k_test['question'])):
            prompt_q = prompt_engineering(q)

            response = completion_with_backoff(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Follow the given examples and answer the question."},
                    {"role": "user", "content": prompt_q},
                ]
            )
            ans_model = response['choices'][0]['message']['content']
            ans_, residual = extract_ans(ans_model)

            fd.write('Q: %s\nA_model:\n%s\nA:\n%s\n\n' % (q, ans_, a))
            i += 1

    acc1, _, _, _ = parse_pred_ans('outputs1.txt')

    i = 0
    with open('outputs2.txt', 'w') as fd:
        for q, a in tqdm(zip(gsm8k_test['question'], gsm8k_test['answer']),
                         total=len(gsm8k_test['question'])):
            prompt_q = prompt_engineering(q)

            response = completion_with_backoff(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Follow the given examples and answer the question."},
                    {"role": "user", "content": prompt_q},
                ]
            )
            ans_model = response['choices'][0]['message']['content']
            ans_, residual = extract_ans(ans_model)

            fd.write('Q: %s\nA_model:\n%s\nA:\n%s\n\n' % (q, ans_, a))
            i += 1

    acc2, _, _, _ = parse_pred_ans('outputs2.txt')


